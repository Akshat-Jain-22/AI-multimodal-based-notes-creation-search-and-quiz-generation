"""
Retrieval + grounded Q&A, built with LangChain (Chroma vector store,
ChatGroq, and LCEL runnables).

Retrieval mode: instead of a fixed top_k, the default is a SCORE THRESHOLD —
return every passage scoring at or above the threshold, since a fixed count
either truncates genuinely relevant content (a broad topic with many relevant
passages) or pads in irrelevant filler (a narrow topic with few). An optional
max_results cap is kept as a safety valve so an overly generous threshold on
a large corpus can't blow up the LLM's context window; top_k mode is still
available for callers that specifically want a bounded count.

Compound-query handling (split_into_subqueries / round-robin merge) is kept
as custom Python wrapped in a RunnableLambda — that logic is specific to
this project and isn't something a stock LangChain component does out of
the box.
"""

import json
import os
import re

from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnableParallel, RunnablePassthrough

from translate_notes import resolve_language_name

load_dotenv()

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
PERSIST_DIR = "chroma_db"
COLLECTION_NAME = "lecture_notes"

# Starting point based on scores observed on the real Thevenin/Norton corpus
# (relevant passages scored ~0.39–0.63 there). Retrieval quality is corpus-
# and embedding-model-dependent, so treat this as a tunable knob, not a fixed
# constant — revisit once you have more lectures indexed and can see whether
# genuinely irrelevant passages start slipping in above this line.
DEFAULT_SCORE_THRESHOLD = 0.35
DEFAULT_MAX_RESULTS = 25

_vectorstore = None


def get_vectorstore(persist_directory=PERSIST_DIR):
    global _vectorstore
    if _vectorstore is None:
        embeddings = HuggingFaceEmbeddings(
            model_name=MODEL_NAME,
            encode_kwargs={"normalize_embeddings": True}
        )
        _vectorstore = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=embeddings,
            persist_directory=persist_directory,
            collection_metadata={"hnsw:space": "cosine"},
        )
    return _vectorstore


def _collection_size(vectorstore):
    return len(vectorstore.get()["ids"])


def _build_lecture_filter(lecture_id_filter):
    """lecture_id_filter can be None, a single lecture_id string, or a list/
    tuple/set of lecture_ids (e.g. every lecture in a class, for multi-tenant
    scoping). A list of exactly one id collapses to a plain equality filter;
    Chroma's $in operator only kicks in when there's genuinely more than one."""
    if not lecture_id_filter:
        return None
    if isinstance(lecture_id_filter, (list, tuple, set)):
        ids = list(lecture_id_filter)
        if not ids:
            return None
        return {"lecture_id": ids[0]} if len(ids) == 1 else {"lecture_id": {"$in": ids}}
    return {"lecture_id": lecture_id_filter}


def doc_to_result(doc, score):
    diagram_images = json.loads(doc.metadata.get("diagram_images_json", "[]"))
    return {
        "score": float(score),
        "lecture_id": doc.metadata["lecture_id"],
        "lecture_title": doc.metadata["lecture_title"],
        "section_heading": doc.metadata["section_heading"],
        "text": doc.page_content,
        "diagram_images": diagram_images,
    }


def search(query, score_threshold=None, top_k=None, max_results=DEFAULT_MAX_RESULTS,
           lecture_id_filter=None, persist_directory=PERSIST_DIR):
    """Single-query similarity search — the atomic operation the compound-
    query retrieval Runnable below is built on top of.

    Two modes:
    - score_threshold given (or neither arg given, using the default
      threshold): returns ALL passages scoring >= threshold, capped at
      max_results as a safety valve.
    - top_k given explicitly (and no threshold): returns exactly the top_k
      highest-scoring passages, old fixed-count behavior — kept for callers
      that specifically want a bounded count regardless of relevance.
    """
    vectorstore = get_vectorstore(persist_directory)
    filter_kwarg = _build_lecture_filter(lecture_id_filter)

    if top_k is not None and score_threshold is None:
        docs_with_scores = vectorstore.similarity_search_with_relevance_scores(
            query, k=top_k, filter=filter_kwarg
        )
        return [doc_to_result(doc, score) for doc, score in docs_with_scores]

    threshold = score_threshold if score_threshold is not None else DEFAULT_SCORE_THRESHOLD
    fetch_k = min(_collection_size(vectorstore), max_results * 4) or 1
    docs_with_scores = vectorstore.similarity_search_with_relevance_scores(
        query, k=fetch_k, filter=filter_kwarg
    )
    above_threshold = [(d, s) for d, s in docs_with_scores if s >= threshold]

    return [doc_to_result(doc, score) for doc, score in above_threshold[:max_results]]


def split_into_subqueries(query):
    """Split a compound query on conjunctions/commas into separate concepts,
    since embedding a whole compound phrase as one vector can under-serve one
    side of it. Always returns the ORIGINAL, unsplit query as the first
    candidate too — a safety net against naive splitting losing shared
    context (e.g. "voltage and current sources" -> "voltage" alone)."""
    if not query or not query.strip():
        return []

    variants = [query.strip()]

    parts = re.split(r"\s+and\s+|,\s*", query, flags=re.IGNORECASE)
    parts = [p.strip() for p in parts if p.strip()]

    if len(parts) > 1:
        variants.extend(parts)

    return variants


def _search_multi(inputs):
    """inputs: {"query": str, "score_threshold": float|None, "top_k": int|None,
                "max_results": int, "lecture_id_filter": str|None}

    Retrieves each subquery variant independently (in threshold mode, ALL
    relevant passages per variant, not just a handful), then merges results
    ROUND-ROBIN so each concept in a compound query gets fair representation
    before the overall max_results cap is applied — otherwise one concept
    with generally higher scores could crowd out another that's genuinely
    relevant but scores lower on an absolute scale."""
    query = inputs["query"]
    score_threshold = inputs.get("score_threshold")
    top_k = inputs.get("top_k")
    max_results = inputs.get("max_results", DEFAULT_MAX_RESULTS)
    lecture_id_filter = inputs.get("lecture_id_filter")

    variants = split_into_subqueries(query)
    if not variants:
        return []

    per_variant_results = [
        search(v, score_threshold=score_threshold, top_k=top_k, max_results=max_results,
               lecture_id_filter=lecture_id_filter)
        for v in variants
    ]

    seen_keys = set()
    merged = []
    max_len = max((len(r) for r in per_variant_results), default=0)
    cap = top_k if (top_k is not None and score_threshold is None) else max_results

    for rank in range(max_len):
        for results in per_variant_results:
            if rank >= len(results):
                continue
            r = results[rank]
            key = (r["lecture_id"], r["section_heading"], r["text"][:50])
            if key in seen_keys:
                continue
            seen_keys.add(key)
            merged.append(r)
            if len(merged) >= cap:
                break
        if len(merged) >= cap:
            break

    merged.sort(key=lambda r: r["score"], reverse=True)
    return merged


# A proper Runnable, composable with `|` like any other LCEL step, and
# directly reusable from generate_quiz.py's retrieval chain.
retrieval_runnable = RunnableLambda(_search_multi)


def search_multi(query, score_threshold=None, top_k=None, max_results=DEFAULT_MAX_RESULTS,
                  lecture_id_filter=None):
    """Thin convenience wrapper so existing call sites can keep calling this
    with plain args instead of building the input dict themselves."""
    return retrieval_runnable.invoke({
        "query": query,
        "score_threshold": score_threshold,
        "top_k": top_k,
        "max_results": max_results,
        "lecture_id_filter": lecture_id_filter,
    })


def format_docs(results):
    if not results:
        return "NO_RESULTS"
    return "\n\n".join(
        f"[Source: {r['lecture_title']} — {r['section_heading']}]\n{r['text']}"
        for r in results
    )


ANSWER_PROMPT = ChatPromptTemplate.from_template("""Answer the student's question using ONLY the source passages below. Cite which
lecture/section each part of your answer comes from (e.g. "as covered in [Lecture Title —
Section]"). If the passages don't fully answer the question, say what's missing rather than
guessing or using outside knowledge.
{language_instruction}
Student's question: {question}

Source passages:
{context}

Answer:""")

llm = ChatGroq(model="openai/gpt-oss-120b", max_tokens=800)

# The full retrieval + grounded-answer pipeline as one LCEL chain. Retrieval
# happens once and its output ("sources") is reused both to build the LLM's
# context and to hand back to the caller for display. CLI-only (see the
# __main__ loop at the bottom) — always answers in English, so
# language_instruction is hardcoded empty here rather than threaded through.
qa_chain = (
    RunnableParallel({
        "sources": RunnableLambda(lambda q: retrieval_runnable.invoke({"query": q})),
        "question": RunnablePassthrough(),
    })
    | RunnableParallel({
        "sources": lambda x: x["sources"],
        "answer": (
            RunnableLambda(lambda x: {
                "context": format_docs(x["sources"]), "question": x["question"], "language_instruction": ""
            })
            | ANSWER_PROMPT
            | llm
            | StrOutputParser()
        ),
    })
)


# ---------------------------------------------------------------------------
# Language support — mirrors the approach in generate_quiz.py, but with one
# extra step: MODEL_NAME ("all-MiniLM-L6-v2") is an English-only embedding
# model, so a query typed in another language would embed poorly against
# this project's English-language index. Retrieval therefore always runs on
# an English version of the query (translated on the fly if needed); only
# the FINAL answer generation is localized into the student's language. The
# retrieved source passages themselves are left in English — translating
# snippets nobody asked to read closely would be wasted LLM cost for little
# benefit, unlike lecture notes (which a student reads start to end).
# ---------------------------------------------------------------------------

ANSWER_LANGUAGE_INSTRUCTION_TEMPLATE = """
Write your entire answer in {language}. Keep technical terms, variable-style names (e.g. R_TH,
V_OC), numeric values, and units as-is — translate only the surrounding natural-language
explanation.
"""

QUERY_TRANSLATION_PROMPT = ChatPromptTemplate.from_template(
    "Translate the following student question into English. Preserve its exact meaning, and keep "
    "any technical terms or variable-style names (e.g. R_TH, V_OC) as-is. Return ONLY the "
    "translated question text, nothing else — no quotes, no commentary.\n\n"
    "Question ({language}): {query}\n\nEnglish translation:"
)

NO_RESULTS_PROMPT = ChatPromptTemplate.from_template(
    "Reply with ONE short sentence in {language}, telling a student that no relevant lecture "
    "content was found for their question. Do not restate the question, add a greeting, or add "
    "any other commentary — output ONLY that one sentence.\n\nAnswer:"
)


def _answer_language_instruction(language):
    language_name = resolve_language_name(language)
    if not language or language_name.strip().lower() == "english":
        return ""
    return ANSWER_LANGUAGE_INSTRUCTION_TEMPLATE.format(language=language_name)


def _translate_query_for_retrieval(query, language_name, retries=2):
    """Best-effort translation of a non-English query into English for
    retrieval purposes only — the original query is still what gets shown
    back to the student and passed to the answer-generation step. Falls
    back to searching with the original-language query on failure (reduced
    recall against an English index, but not a crash)."""
    for attempt in range(retries):
        try:
            translated = (QUERY_TRANSLATION_PROMPT | llm | StrOutputParser()).invoke(
                {"language": language_name, "query": query}
            )
            translated = translated.strip().strip('"')
            return translated if translated else query
        except Exception as e:
            if attempt < retries - 1:
                continue
            print(f"Warning: failed to translate query into English for retrieval ({e}); "
                  f"searching with the original-language query instead (may reduce recall).")
            return query


def _localized_no_results_message(language_name):
    try:
        return (NO_RESULTS_PROMPT | llm | StrOutputParser()).invoke({"language": language_name}).strip()
    except Exception as e:
        print(f"Warning: failed to localize the 'no results' message into {language_name}: {e}")
        return "No relevant content found for this query."


def answer_query(query, lecture_id_filter=None, max_tokens=800, language="en"):
    """Retrieval + grounded answer, scoped to lecture_id_filter (typically
    every lecture_id in one class, for multi-tenant isolation). Used by
    api.py's /search endpoint — qa_chain above is left untouched since it's
    still used by this file's own CLI loop and takes a plain query string
    with no scoping.

    `language` is a code like 'hi' (see db.py's users.preferred_language).
    Retrieval always runs in English (see module-level comment above);
    only the final answer is written in `language`."""
    language_name = resolve_language_name(language)
    needs_translation = language and language_name.strip().lower() != "english"

    retrieval_query = _translate_query_for_retrieval(query, language_name) if needs_translation else query
    sources = search_multi(retrieval_query, lecture_id_filter=lecture_id_filter)

    if not sources:
        answer = (
            _localized_no_results_message(language_name)
            if needs_translation else
            "No relevant content found for this query."
        )
        return {"sources": [], "answer": answer}

    context = format_docs(sources)
    language_instruction = _answer_language_instruction(language)
    answer = (ANSWER_PROMPT | llm | StrOutputParser()).invoke({
        "question": query, "context": context, "language_instruction": language_instruction
    })
    return {"sources": sources, "answer": answer}


def generate_grounded_answer(query, results, max_tokens=800, language="en"):
    """Kept for callers that already have a retrieved result set in hand."""
    if not results:
        return (
            _localized_no_results_message(resolve_language_name(language))
            if language and language != "en" else
            "No relevant content found for this query."
        )
    context = format_docs(results)
    language_instruction = _answer_language_instruction(language)
    return (ANSWER_PROMPT | llm | StrOutputParser()).invoke({
        "question": query, "context": context, "language_instruction": language_instruction
    })


if __name__ == "__main__":
    print("=== Notes Search (LangChain + Chroma, threshold-based retrieval) ===")
    print("(type 'quit' to exit)\n")

    while True:
        query = input("Search query: ").strip()
        if query.lower() in ("quit", "exit"):
            break
        if not query:
            continue

        result = qa_chain.invoke(query)

        print(f"\n{len(result['sources'])} matching passage(s) above threshold ({DEFAULT_SCORE_THRESHOLD}):")
        for r in result["sources"]:
            print(f"  [{r['score']:.3f}] {r['lecture_title']} — {r['section_heading']}")

        print("\nGenerating grounded answer...\n")
        print(result["answer"])
        print("\n" + "-" * 60 + "\n")