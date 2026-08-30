"""
Builds/updates a persistent Chroma vector store from search_passages.json,
replacing the earlier raw .npz + manual cosine-similarity implementation.

Re-indexing is REPLACE, not MERGE, at the lecture_id level: before adding
new_passages, every existing passage belonging to any lecture_id present in
new_passages is deleted first, then the full new set is added fresh. This
matters because passage ids are "{lecture_id}::{section_heading}::{i}"
(chunk_notes_for_search.py) and section_heading comes from an LLM, which
isn't deterministic across runs — re-processing the same lecture can produce
slightly reworded headings, which used to mean the old "skip ids already
present" dedup logic silently left stale passages behind under their old
ids instead of replacing them. Wiping by lecture_id prefix first sidesteps
relying on exact id stability entirely. Passages from OTHER lecture_ids not
present in this call are untouched, so accumulating across different
lectures still works as before.
"""

import json
import sys
import os

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
PERSIST_DIR = "chroma_db"
COLLECTION_NAME = "lecture_notes"


def _cosine_relevance_score_fn(distance: float) -> float:
    """Corrects a known langchain_chroma miscalibration for cosine space
    (see e.g. langchain-ai/langchain issues #18709 and #10864 — the latter
    reproduced with this exact setup: all-MiniLM-L6-v2 + normalize_
    embeddings=True). Chroma's cosine DISTANCE is 1 - cosine_similarity,
    ranging [0, 2]. LangChain's built-in cosine relevance function instead
    returns `1 - distance` directly, which algebraically equals raw cosine
    SIMILARITY again (range [-1, 1]) — not a score genuinely normalized to
    [0, 1] the way the "relevance score" API promises and the way
    DEFAULT_SCORE_THRESHOLD in search_notes.py is meant to be compared
    against. This is the actual "scores not cleanly in [0,1]" bug — not
    something specific to this project's data.

    This maps distance to a true [0, 1] score instead:
        1 - distance/2  ==  (1 + cosine_similarity) / 2
    which linearly maps cosine_similarity's real range [-1, 1] onto [0, 1],
    with 0.5 meaning genuinely orthogonal/unrelated content — not an
    arbitrary number that happens to fall in the middle of a mis-scaled range.
    """
    return 1.0 - distance / 2.0


def get_vectorstore(persist_directory=PERSIST_DIR):
    embeddings = HuggingFaceEmbeddings(
        model_name=MODEL_NAME,
        encode_kwargs={"normalize_embeddings": True}
    )
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=persist_directory,
        relevance_score_fn=_cosine_relevance_score_fn,
        collection_metadata={"hnsw:space": "cosine"},
    )


def passage_to_document(passage):
    metadata = {
        "lecture_id": passage["lecture_id"],
        "lecture_title": passage["lecture_title"],
        "section_heading": passage["section_heading"],
        "diagram_images_json": json.dumps(passage.get("diagram_images", []))
    }
    return Document(page_content=passage["text"], metadata=metadata, id=passage["id"])


def build_index(passages_path, persist_directory=PERSIST_DIR):
    with open(passages_path, "r", encoding="utf-8") as f:
        new_passages = json.load(f)

    if not new_passages:
        print("No passages to index.")
        return

    vectorstore = get_vectorstore(persist_directory)
    lecture_ids_in_batch = set(p["lecture_id"] for p in new_passages)
    all_ids = vectorstore.get()["ids"]
    stale_ids = [
        i for i in all_ids
        if i.split("::", 1)[0] in lecture_ids_in_batch
    ]
    if stale_ids:
        vectorstore.delete(ids=stale_ids)
        print(f"Removed {len(stale_ids)} existing passage(s) for "
              f"{', '.join(sorted(lecture_ids_in_batch))} before re-indexing "
              f"(handles LLM-generated section headings changing between runs).")

    documents = [passage_to_document(p) for p in new_passages]
    ids = [d.id for d in documents]

    print(f"Embedding {len(documents)} passage(s)...")
    vectorstore.add_documents(documents, ids=ids)

    all_metadata = vectorstore.get()["metadatas"]
    lecture_ids = sorted(set(m["lecture_id"] for m in all_metadata))
    print(f"Index now has {len(all_metadata)} total passages across "
          f"{len(lecture_ids)} lecture(s): {', '.join(lecture_ids)}")
    print(f"Saved to Chroma store at {persist_directory}/")


if __name__ == "__main__":
    passages_path = sys.argv[1] if len(sys.argv) > 1 else "search_passages.json"
    persist_directory = sys.argv[2] if len(sys.argv) > 2 else PERSIST_DIR

    build_index(passages_path, persist_directory)