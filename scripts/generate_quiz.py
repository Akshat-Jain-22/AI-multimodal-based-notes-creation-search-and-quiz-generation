"""
Quiz generation, rebuilt with LangChain: Pydantic schemas + structured
output (via ChatGroq's tool-calling) replace the old manual json.loads() +
regex JSON-repair approach entirely — including fix_latex_json_escapes(),
which existed only to patch broken JSON text and is no longer needed once
the LLM returns already-parsed, schema-validated Python objects.

Retrieval reuses search_notes.py's retrieval_runnable directly (threshold-
based, compound-query-aware) instead of duplicating that logic here, which
is what the old get_topic_content_via_rag / split_topic_into_subtopics used
to do.
"""

import sys
import os
import re
import json
import random
from typing import Optional, Union, List, Literal, Annotated

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from groq import BadRequestError, APIStatusError
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

from search_notes import retrieval_runnable, PERSIST_DIR
from render_circuit_diagram import render_circuit_svg, circuit_caption, unique_diagram_path
from render_chart_diagram import render_chart, chart_caption, unique_chart_path

load_dotenv()


# ---------------------------------------------------------------------------
# Structured output schemas. These replace the old hand-written JSON
# structure documentation in prompts — the schema itself tells the LLM
# (via Groq's tool-calling) exactly what shape to return, and LangChain
# validates/parses the response into real Python objects automatically.
# ---------------------------------------------------------------------------

class DiagramComponent(BaseModel):
    type: Literal["resistor", "voltage_source", "current_source"]
    label: str
    value: str


class CircuitDiagramSpec(BaseModel):
    kind: Literal["circuit"] = "circuit"
    components: List[DiagramComponent]
    terminal_labels: List[str] = Field(default_factory=lambda: ["A", "B"])


class ChartPoint(BaseModel):
    x: float
    y: float


class ChartDiagramSpec(BaseModel):
    kind: Literal["chart"] = "chart"
    chart_type: Literal["bar", "line", "pie", "scatter"]
    title: Optional[str] = None
    x_label: Optional[str] = None
    y_label: Optional[str] = None
    categories: Optional[List[str]] = None
    values: Optional[List[float]] = None
    labels: Optional[List[str]] = None
    points: Optional[List[ChartPoint]] = None


DiagramSpec = Annotated[Union[CircuitDiagramSpec, ChartDiagramSpec], Field(discriminator="kind")]


class Question(BaseModel):
    question: str
    # Scratch-work field, generated FIRST (field order matters for structured
    # output — Groq generates JSON fields in schema order). Without this, the
    # model was observed committing to correct_answer_index before doing any
    # actual arithmetic, then spiraling into long, self-contradictory
    # "explanation" text trying to reconcile a wrong pre-committed answer
    # with its real calculation. Forcing the math to happen here first, then
    # popped before output, fixes that failure mode.
    reasoning: Optional[str] = Field(
        default=None,
        description="Private step-by-step calculation, computed BEFORE deciding on options/answer. Not shown to students."
    )
    # mcq
    options: Optional[List[str]] = None
    correct_answer_index: Optional[int] = None
    explanation: Optional[str] = None
    # one_word (also uses explanation above)
    correct_answer: Optional[str] = None
    # short_answer / long_answer
    expected_answer_summary: Optional[str] = None
    # populated only for questions that genuinely warrant an image
    diagram_spec: Optional[DiagramSpec] = None


class QuestionSet(BaseModel):
    questions: List[Question]


class QuizRequest(BaseModel):
    topic: str = Field(default="", description="The subject/concept requested, in the student's own words")
    format: Literal["mcq", "one_word", "short_answer", "long_answer"] = "mcq"
    content_type: Literal["theory", "numerical", "derivation", "descriptive"] = "theory"
    difficulty: Literal["easy", "medium", "hard"] = "medium"
    count: Union[int, Literal["all"]] = 5
    needs_diagram: bool = False


# ---------------------------------------------------------------------------
# Prompt content
# ---------------------------------------------------------------------------

FORMAT_FIELD_GUIDE = {
    "mcq": (
        'FIRST, in "reasoning", work out the exact numeric answer step by step (if applicable). '
        'THEN populate "options" with exactly 4 choices where exactly one matches your computed '
        'answer, "correct_answer_index" (0-3) pointing to it, and a CONCISE "explanation" (2-4 '
        'sentences stating the method and final answer — do not repeat or re-derive the '
        'calculation multiple times, and do not second-guess an answer you already computed in '
        '"reasoning"). Leave correct_answer and expected_answer_summary unset.'
    ),
    "one_word": (
        'FIRST, in "reasoning", work out the answer. THEN populate "correct_answer" (a single '
        'word or short phrase) and a CONCISE "explanation" (2-4 sentences, not a re-derivation). '
        'Leave options, correct_answer_index, and expected_answer_summary unset.'
    ),
    "short_answer": (
        'Populate "expected_answer_summary" (2-4 sentences covering what a correct answer must '
        'include). Leave the other answer fields unset.'
    ),
    "long_answer": (
        'Populate "expected_answer_summary" (a fuller outline of the expected answer, including '
        'key steps/points a strong answer should cover — for derivations, list the expected '
        'derivation steps in order). Leave the other answer fields unset.'
    ),
}

CONTENT_TYPE_GUIDE = {
    "theory": "Every question must test conceptual understanding — definitions, relationships, why something works. Do NOT include numerical calculations.",
    "numerical": (
        "EVERY question must require an actual numeric calculation. Invent NEW plausible values "
        "consistent with the concepts and formulas in the content — do not just reuse an exact "
        "example already shown. Provide the correct final numeric answer, and for long_answer "
        "format, the full solution steps."
    ),
    "derivation": (
        "EVERY question must ask the student to derive a formula/result from first principles, or "
        "walk through the steps of a method, exactly as covered in the content."
    ),
    "descriptive": "Every question must ask the student to explain, compare, or discuss a concept in their own words, in prose.",
}

DIFFICULTY_GUIDE = {
    "easy": (
        "The student substitutes GIVEN values directly into ONE known formula and solves. "
        "Example: \"Given V_OC=20V and I_SC=4A, find R_TH\" (one formula, one step)."
    ),
    "medium": (
        "Do NOT directly hand over V_TH, R_TH, V_OC, or I_SC as given values — UNLESS that value "
        "is itself the final thing being asked for. Instead, describe the underlying circuit itself "
        "(a specific voltage/current source and resistor values), so the student must first derive "
        "V_TH and/or R_TH THEMSELVES as an intermediate step, then use that result to answer what's "
        "actually asked (e.g. load voltage, load current, Norton current). This — deriving an "
        "intermediate quantity before using it — is what makes a question medium rather than easy. "
        "A question that hands over V_TH/R_TH directly and asks for one more plug-in step is EASY, "
        "not medium, no matter how tedious the arithmetic is. Ask about exactly ONE quantity per "
        "question — never blend two different quantities together in one question's wording (e.g. "
        "do not ask for 'the Thevenin voltage across the load resistor'; that conflates V_TH, which "
        "is a property of the source network alone, with V_L, the actual loaded voltage — these are "
        "different numbers. Ask for one or the other, using its precise name)."
    ),
    "hard": (
        "Same requirement as medium (derive intermediate quantities from raw circuit component "
        "values, never hand them over directly), PLUS at least one of: 3+ chained calculation "
        "steps, a non-obvious application not directly demonstrated in the source content, an edge "
        "case, or synthesizing multiple concepts/theorems together (e.g. combining Thevenin AND "
        "Norton analysis, or maximum power transfer alongside a Thevenin equivalent)."
    ),
}

DIFFICULTY_REMINDER = """
REMINDER before you finalize: for medium/hard numerical questions, do NOT directly state V_TH,
R_TH, V_OC, or I_SC as given values unless that's the exact unknown being solved for — describe
the underlying circuit's actual source/resistor values instead, so the student must derive these
themselves as an intermediate step. Check each question: if it hands over V_TH/R_TH directly and
only needs one more formula to finish, that question is actually EASY — revise it before
finalizing.
"""

FORMULA_FORMATTING_NOTE = """
Write all formulas and mathematical notation in PLAIN TEXT, not LaTeX. Do NOT use backslash
commands (no \\frac, \\cdot, \\Omega, \\Delta, \\times, etc.) anywhere in your response — a single
incorrectly-escaped backslash will make your entire response invalid, since it's parsed as JSON.
Instead write formulas plainly, for example:
- "R_TH = V_OC / I_SC" instead of LaTeX \\frac notation
- "V_TH * R_L / (R_L + R_TH)" instead of a LaTeX fraction
- the word "ohm"/"ohms" instead of \\Omega
- underscores for subscripts (R_TH, V_OC, I_SC) rather than LaTeX braces
"""

DIAGRAM_GUIDANCE = """
Diagram-based questions were specifically requested. For questions that involve CONCRETE NUMERIC
values (actual numbers explicitly stated in that question's own text), you MUST populate
diagram_spec for that question — do not skip it just because the field is optional in the schema:
- Use a CIRCUIT spec for electronics/circuit questions with concrete numeric component values.
- Use a CHART spec for questions with concrete numeric data, proportions, or plotted points.
- Every number and label inside diagram_spec MUST exactly match the numbers stated in that
  question's own text.

For SYMBOLIC or purely conceptual/derivation questions with no actual numbers (e.g. "derive R_TH
in terms of V_OC and I_SC", or describing a graphical METHOD without concrete data points), leave
diagram_spec UNSET (null). Never invent placeholder numeric values just to force a diagram, and
never put a non-numeric string (like a variable name such as "V_TH") where a number is expected —
if you can't fill every numeric field with an actual number, leave diagram_spec unset instead.
"""

DIAGRAM_REMINDER = """
REMINDER before you finalize: diagrams were explicitly requested for this quiz. Check EVERY
question one more time — if it states concrete numeric values (e.g. "10 ohms", "15V"), that
question's diagram_spec MUST be populated with those exact values. Leaving diagram_spec empty on a
numeric question is a mistake, not a valid choice, even though the field is technically optional.
"""

FORMAT_REMINDER_TEMPLATE = """
REMINDER before you finalize: every single question MUST use the "{fmt}" fields described above,
with no exceptions or substitutions. Do not fill in expected_answer_summary for a question that
should have options/correct_answer_index (or vice versa) — check each question against the format
guide one more time before finishing.
"""


def build_prompt(retrieved_results, request, topic, needs_diagram=False):
    fmt = request["format"]
    content_type = request.get("content_type", "theory")
    difficulty = request.get("difficulty", "medium")
    count = request.get("count", 5)

    if isinstance(count, str) and count.lower() == "all":
        count_instruction = (
            "Generate EVERY distinct, meaningful question that could reasonably be asked about this "
            "content — cover all key facts, formulas, relationships, and (for numerical/derivation "
            "sets) all the distinct calculation/derivation types shown or implied. Do not pad with "
            "repetitive or trivial variations, but do not artificially limit the count either."
        )
    else:
        count_instruction = f"Generate EXACTLY {count} questions."

    sources_seen = sorted(set(f"{r['lecture_title']} — {r['section_heading']}" for r in retrieved_results))
    content_block = "\n\n".join(
        f"[Source: {r['lecture_title']} — {r['section_heading']}]\n{r['text']}"
        for r in retrieved_results
    )

    topic_note = (
        f'You are restricted to the topic: "{topic}". Do not ask about anything outside this topic. '
        f"The retrieved content below may span multiple lectures — that is expected; cover the topic "
        f"comprehensively using all of it."
        if topic else
        "Cover the content below broadly."
    )

    diagram_instructions = DIAGRAM_GUIDANCE if needs_diagram else ""
    diagram_reminder = DIAGRAM_REMINDER if needs_diagram else ""
    difficulty_reminder = (
        DIFFICULTY_REMINDER if content_type == "numerical" and difficulty in ("medium", "hard") else ""
    )

    difficulty_note = DIFFICULTY_GUIDE.get(difficulty, "")
    format_reminder = FORMAT_REMINDER_TEMPLATE.format(fmt=fmt)

    prompt = f"""You are an experienced teacher creating quiz/assignment questions from lecture
content retrieved for a specific topic. Use ONLY the content below as your source for concepts,
definitions, and formulas — do not introduce topics not covered here.
{FORMULA_FORMATTING_NOTE}
{topic_note}

Sources this content was drawn from:
{chr(10).join('- ' + s for s in sources_seen)}
{diagram_instructions}
Question format: {fmt}
{FORMAT_FIELD_GUIDE[fmt]}

Question type: {content_type}
{CONTENT_TYPE_GUIDE[content_type]}

Difficulty: {difficulty}
{difficulty_note}

{count_instruction}
{diagram_reminder}{difficulty_reminder}{format_reminder}
Retrieved content:
{content_block}
"""
    return prompt


def _parse_numeric(text):
    """Extract a single float from a string like '20V', '10 ohm', '0.5 amps',
    or a fraction like '160 / 17 volts'. Returns None if no number is found."""
    if not isinstance(text, str):
        return None
    text = text.strip()

    frac_match = re.match(r"^\s*(-?\d+(?:\.\d+)?)\s*/\s*(-?\d+(?:\.\d+)?)\b", text)
    if frac_match:
        num, den = float(frac_match.group(1)), float(frac_match.group(2))
        if den != 0:
            return num / den

    num_match = re.search(r"-?\d+(?:\.\d+)?", text)
    return float(num_match.group()) if num_match else None


def shuffle_mcq_options(question_dict):
    """Randomize which position the correct option lands in.

    Nothing in the generation prompt tells the model WHERE to place the
    correct answer among the 4 options, and nothing downstream previously
    randomized the final order — so the option order shipped was whatever
    the model naturally tended to produce. That's model-dependent and can
    be badly skewed (observed: gpt-oss-120b defaulting to placing the
    correct answer first on nearly every question), which makes the quiz
    trivially gameable by position regardless of whether the underlying
    answer is correct. This shuffles the options and keeps
    correct_answer_index pointing at the right one, so position carries
    no information either way.
    """
    options = question_dict.get("options")
    idx = question_dict.get("correct_answer_index")
    if not options or idx is None or not (0 <= idx < len(options)):
        return

    order = list(range(len(options)))
    random.shuffle(order)
    question_dict["options"] = [options[i] for i in order]
    question_dict["correct_answer_index"] = order.index(idx)


def verify_series_circuit_answer(question_dict):
    """LLM arithmetic on multi-step circuit problems is unreliable even once
    the model's reasoning is self-consistent (self-consistency isn't the
    same as correctness). Since diagram_spec only ever describes a simple
    series chain (that's all render_circuit_svg supports), we already have
    everything needed to compute the real answer ourselves in plain Python
    and cross-check the model's chosen option against it.

    Checks against WHICHEVER quantity the question text actually asks about
    (Thevenin resistance, Thevenin voltage, load current, or load voltage) —
    not just load voltage/current — since many of these questions ask for
    R_TH or V_TH directly. Only handles the topology this project actually
    generates: one voltage source, one or more series resistors, with the
    LAST resistor treated as the load.

    Auto-corrects correct_answer_index if a different option matches the
    real computed value (and updates the explanation to match, so the answer
    key doesn't contradict itself); prints a note either way so nothing
    happens silently. Returns True if checked (and possibly corrected),
    False if unverifiable this way — False means "unverified", not "wrong";
    a human should still spot-check it.
    """
    diagram_spec = question_dict.get("diagram_spec")
    options = question_dict.get("options")
    if not diagram_spec or diagram_spec.get("kind") != "circuit" or not options:
        return False

    components = diagram_spec.get("components", [])
    voltage_sources = [c for c in components if c.get("type") == "voltage_source"]
    resistors = [c for c in components if c.get("type") == "resistor"]
    if len(voltage_sources) != 1 or len(resistors) < 1:
        return False  # only the single-source series case is handled

    v_values = [_parse_numeric(v.get("value")) for v in voltage_sources]
    r_values = [_parse_numeric(r.get("value")) for r in resistors]
    if any(v is None for v in v_values) or any(r is None for r in r_values):
        return False

    v_source = v_values[0]
    r_load = r_values[-1]
    r_th = sum(r_values[:-1])
    if r_load + r_th <= 0:
        return False

    v_load = v_source * r_load / (r_load + r_th)
    i_load = v_source / (r_load + r_th)
    # For this pure series topology, V_TH as seen from the load terminals
    # equals the source voltage exactly — removing the load breaks the only
    # loop, so no current flows and there's no drop across the other
    # resistors before that point.
    v_th = v_source

    q_lower = (question_dict.get("question") or "").lower()
    candidates = []
    if "thevenin resistance" in q_lower or "r_th" in q_lower:
        candidates.append(("Thevenin resistance", r_th))
    if "thevenin voltage" in q_lower or "v_th" in q_lower or "open-circuit voltage" in q_lower or "open circuit voltage" in q_lower:
        candidates.append(("Thevenin voltage", v_th))
    if "load current" in q_lower or "current through the load" in q_lower:
        candidates.append(("load current", i_load))
    if "load voltage" in q_lower or "voltage across the load" in q_lower or "voltage across" in q_lower:
        candidates.append(("load voltage", v_load))
    if not candidates:
        # question text didn't clearly say which quantity — try the two most
        # common asks as a fallback
        candidates = [("load voltage", v_load), ("load current", i_load)]

    option_values = [_parse_numeric(opt) for opt in options]

    def find_match(target):
        for idx, val in enumerate(option_values):
            if val is not None and abs(val - target) < max(0.05, 0.02 * abs(target)):
                return idx
        return None

    match_idx, matched_label, matched_value = None, None, None
    for label, target in candidates:
        idx = find_match(target)
        if idx is not None:
            match_idx, matched_label, matched_value = idx, label, target
            break

    question_preview = (question_dict.get("question") or "")[:80]

    if match_idx is None:
        checked = ", ".join(f"{label}={val:.4g}" for label, val in candidates)
        print(f"Note: could not verify this question against the circuit's own values "
              f"(checked {checked}, none matches any offered option) — please review "
              f"manually: \"{question_preview}...\"")
        return False

    stated_idx = question_dict.get("correct_answer_index")
    if stated_idx != match_idx:
        stated_label = chr(65 + stated_idx) if isinstance(stated_idx, int) else "?"
        print(f"Note: auto-corrected an answer using independent circuit calculation "
              f"(model chose option {stated_label}, but option {chr(65+match_idx)} matches "
              f"the circuit's own values: {matched_label} = {matched_value:.4g}) — "
              f"\"{question_preview}...\"")
        question_dict["correct_answer_index"] = match_idx
        # Keep the explanation consistent with the corrected answer instead
        # of leaving it pointing at the model's original (wrong) value.
        old_explanation = (question_dict.get("explanation") or "").rstrip()
        question_dict["explanation"] = (
            f"{old_explanation} [Corrected: recalculating from the circuit's own stated "
            f"values gives {matched_label} = {matched_value:.4g}, which is option "
            f"{chr(65+match_idx)}.]"
        ).strip()

    return True


def attach_generated_diagrams(questions, output_dir="generated_diagrams"):
    """For every question dict with a 'diagram_spec', render an actual image
    matching its exact values/data and attach it as 'diagram'. Dispatches to
    the circuit renderer or the chart renderer based on diagram_spec['kind'].
    Questions without a diagram_spec are left as-is."""
    diagram_count = 0
    for q in questions:
        spec = q.pop("diagram_spec", None)
        if not spec:
            continue

        kind = spec.get("kind")
        try:
            if kind == "circuit" and spec.get("components"):
                path = unique_diagram_path(output_dir=output_dir)
                render_circuit_svg(spec, path)
                q["diagram"] = {"caption": circuit_caption(spec), "image_file": path}
                diagram_count += 1
            elif kind == "chart":
                path = unique_chart_path(output_dir=output_dir)
                render_chart(spec, path)
                q["diagram"] = {"caption": chart_caption(spec), "image_file": path}
                diagram_count += 1
            else:
                print(f"Warning: unrecognized or incomplete diagram_spec (kind={kind!r}) — "
                      f"skipping diagram for this question.")
        except Exception as e:
            print(f"Warning: failed to render diagram ({e}); leaving that question without a diagram.")

    return diagram_count


def get_topic_content(topic, lecture_id_filter=None, needs_diagram=False, persist_directory=PERSIST_DIR):
    """Retrieve all relevant passages for the topic via the shared, threshold-
    based, compound-query-aware retrieval Runnable from search_notes.py —
    this replaces the old get_topic_content_via_rag / split_topic_into_subtopics
    duplicate implementation entirely.

    When needs_diagram is True, diagram-bearing passages are sorted to the
    front — not because we'll reuse their images, but because such sections
    more often describe something concretely visualizable, giving the LLM
    better grounding for the diagrams it generates."""
    results = retrieval_runnable.invoke({
        "query": topic,
        "lecture_id_filter": lecture_id_filter,
    })

    if needs_diagram:
        results = sorted(results, key=lambda r: bool(r.get("diagram_images")), reverse=True)

    return results


# gpt-oss-120b is a reasoning model: unlike llama-3.3-70b-versatile, its
# internal reasoning tokens are included in the response by default and
# count against max_tokens. reasoning_effort is capped at "low" since the
# schema's own "reasoning" field already makes the model work through each
# answer step-by-step as part of the structured output — full internal
# reasoning depth on top of that mostly just burns tokens without adding
# accuracy here.
#
# max_tokens is NOT a fixed constant here — see _build_quiz_llm() below.
# This project's Groq account is on the on_demand/free tier, which caps
# PROMPT tokens + max_tokens COMBINED at a hard 8000 tokens per request.
# A fixed max_tokens value can't safely serve every request: a plain-text
# topic prompt runs ~2200 input tokens, but a diagram-enabled or broad-topic
# prompt can run ~3600+ — confirmed by hitting Groq's 413 rate_limit_exceeded
# at multiple different fixed max_tokens values as prompt size varied.
# max_tokens is now computed per-request instead, based on the actual
# prompt's estimated size, so it adapts rather than needing to be re-tuned
# by hand every time a bigger request comes through.
_QUIZ_TPM_BUDGET = 6500  # stay under the account's real 8000 cap with margin
_QUIZ_MAX_TOKENS_FLOOR = 2000
_QUIZ_MAX_TOKENS_CEILING = 6000


def _estimate_tokens(text):
    """Rough chars-per-token estimate — NOT a substitute for this model's
    real tokenizer, just good enough to stay under a hard account-level cap.

    Uses 3 chars/token rather than the more typical ~4, because this
    project's retrieved content (circuit/electronics text: Ω, subscripts,
    repeated technical terms, LaTeX-ish notation) tokenizes less
    efficiently than average English prose. A real request that used
    len//4 still exceeded Groq's 8000 TPM cap despite the safety budget
    below it — len//3 combined with a lower _QUIZ_TPM_BUDGET (6500, down
    from 7500) is a more conservative correction, not a precise fix; if
    this project ever adds a real tokenizer (e.g. tiktoken) this whole
    function should be replaced rather than tuned further by hand."""
    return max(1, len(text) // 3)


def _build_quiz_llm(prompt_text):
    """Build a fresh structured-output LLM sized for this specific prompt,
    so max_tokens adapts to actual prompt size instead of being a fixed
    constant that eventually fails on a bigger-than-usual request."""
    estimated_input = _estimate_tokens(prompt_text)
    available = _QUIZ_TPM_BUDGET - estimated_input
    max_tok = max(_QUIZ_MAX_TOKENS_FLOOR, min(_QUIZ_MAX_TOKENS_CEILING, available))

    if available < _QUIZ_MAX_TOKENS_FLOOR:
        print(
            f"Warning: estimated prompt size (~{estimated_input} tokens) leaves less than "
            f"the {_QUIZ_MAX_TOKENS_FLOOR}-token floor for the response, under this "
            f"account's ~{_QUIZ_TPM_BUDGET}-token safety budget. Using the floor anyway, "
            f"but this request is likely to still hit Groq's rate limit — try a narrower "
            f"topic, fewer questions, or disabling diagrams."
        )

    return ChatGroq(
        model="openai/gpt-oss-120b",
        max_tokens=max_tok,
        reasoning_effort="low",
    ).with_structured_output(QuestionSet)


NO_BACKSLASH_REINFORCEMENT = (
    "\n\nYour previous attempt was REJECTED because it contained a backslash character, "
    "which broke JSON parsing. This time, do not use the backslash character (\\) "
    "ANYWHERE in your response, for any reason."
)

DIAGRAM_DISABLE_OVERRIDE = (
    "\n\nIMPORTANT OVERRIDE: set diagram_spec to null for EVERY question, with no exceptions. "
    "Do not attempt to describe any circuit or chart this time — diagrams are disabled for "
    "this generation because earlier attempts failed to produce valid diagram data."
)


def _invoke_with_retries(prompt_variants):
    """Try each prompt variant in order (each one a progressively stricter
    fallback), returning the first successful result along with which
    variant succeeded. A diagram-specific failure (e.g. the model trying to
    force a diagram onto symbolic/non-numeric content) shouldn't cost the
    student the whole quiz — the last variant disables diagrams entirely so
    generation can still succeed.

    Also catches APIStatusError (covers Groq's 413 rate_limit_exceeded when
    a request's prompt+max_tokens exceeds the account's TPM cap) alongside
    BadRequestError (malformed JSON/tool-call responses) — both are reasons
    to fall through to the next, stricter/smaller prompt variant rather than
    crashing outright.
    """
    last_error = None
    for i, prompt in enumerate(prompt_variants):
        try:
            llm_for_this_attempt = _build_quiz_llm(prompt)
            return llm_for_this_attempt.invoke(prompt), i
        except (BadRequestError, APIStatusError) as e:
            last_error = e
            continue
    raise RuntimeError(
        "Quiz generation failed after multiple attempts — either invalid formatting in "
        "the model's response, or the request was too large for this Groq account's rate "
        "limit. Try a smaller question count, a narrower topic, or disabling diagrams, "
        "then try again."
    ) from last_error


def generate_question_set(request, persist_directory=PERSIST_DIR):
    topic = request.get("topic", "")
    lecture_id_filter = request.get("lecture_id")
    needs_diagram = bool(request.get("needs_diagram", False))

    retrieved = get_topic_content(topic, lecture_id_filter=lecture_id_filter,
                                   needs_diagram=needs_diagram, persist_directory=persist_directory)

    if not retrieved:
        raise ValueError(
            f"No indexed content found for topic '{topic}'. "
            f"Make sure build_search_index.py has been run and the topic is reasonably specific."
        )

    base_prompt = build_prompt(retrieved, request, topic, needs_diagram=needs_diagram)

    prompt_variants = [base_prompt, base_prompt + NO_BACKSLASH_REINFORCEMENT]
    if needs_diagram:
        # Diagrams add real failure risk beyond plain JSON formatting (e.g.
        # symbolic/non-numeric content that can't be cleanly diagrammed), so
        # give this case one more fallback: disable diagrams entirely rather
        # than losing the whole quiz over a diagram-specific error.
        prompt_variants.append(base_prompt + NO_BACKSLASH_REINFORCEMENT + DIAGRAM_DISABLE_OVERRIDE)

    question_set, attempt_index = _invoke_with_retries(prompt_variants)

    diagrams_disabled_by_fallback = needs_diagram and attempt_index == len(prompt_variants) - 1 and len(prompt_variants) == 3
    if diagrams_disabled_by_fallback:
        needs_diagram = False
        print(f"Warning: diagram generation repeatedly failed for topic "
              f"'{topic or '(broad search)'}' (often because the content is symbolic/conceptual "
              f"rather than numeric). This quiz was generated WITHOUT diagrams as a fallback.")

    questions = [q.model_dump(exclude_none=True) for q in question_set.questions]
    for q in questions:
        q.pop("reasoning", None)

    # Randomize option order — see shuffle_mcq_options() docstring. Runs
    # before verification below so the "corrected option X" messages there
    # refer to the same option positions the user will actually see.
    if request["format"] == "mcq":
        for q in questions:
            shuffle_mcq_options(q)

    # Independent arithmetic check for simple series-circuit numerical MCQs.
    # Must run BEFORE attach_generated_diagrams, which consumes/replaces
    # diagram_spec's raw component values with just a rendered image path.
    if request["format"] == "mcq" and request.get("content_type") == "numerical":
        for q in questions:
            verify_series_circuit_answer(q)

    if needs_diagram:
        diagram_count = attach_generated_diagrams(questions)
        if diagram_count == 0:
            print(f"Warning: diagram-based questions were requested for topic "
                  f"'{topic or '(broad search)'}', but the model didn't produce any "
                  f"diagram specs to render. Questions were generated without diagrams.")

    sources = sorted(set(f"{r['lecture_title']} — {r['section_heading']}" for r in retrieved))

    return {
        "topic": topic or "(broad search)",
        "sources": sources,
        "format": request["format"],
        "content_type": request.get("content_type", "theory"),
        "difficulty": request.get("difficulty", "medium"),
        "requested_count": request.get("count", 5),
        "questions": questions
    }


def format_questions_as_markdown(result):
    lines = [
        f"# Quiz — {result['topic']}",
        f"*{result['content_type'].title()} | {result['format'].replace('_',' ').title()} | "
        f"{result['difficulty'].title()} difficulty*",
        "",
        "**Sources:** " + "; ".join(result["sources"]),
        ""
    ]

    answer_lines = ["---", "", "## Answer Key", ""]

    fmt = result["format"]
    for i, q in enumerate(result["questions"], start=1):
        lines.append(f"**Q{i}. {q['question']}**")

        diagram = q.get("diagram")
        if diagram:
            img_path = diagram["image_file"].replace("\\", "/")
            caption = diagram.get("caption", "").strip() or f"Diagram for Q{i}"
            lines.append("")
            lines.append(f"![{caption}]({img_path})")
            lines.append(f"*{caption}*")

        lines.append("")

        if fmt == "mcq" and q.get("options") and q.get("correct_answer_index") is not None:
            for j, opt in enumerate(q["options"]):
                lines.append(f"- {chr(65+j)}. {opt}")
            lines.append("")
            correct = chr(65 + q["correct_answer_index"])
            answer_lines.append(f"**Q{i}.** {correct}. {q['options'][q['correct_answer_index']]}")
            answer_lines.append(f"*{q.get('explanation', '')}*")
        elif fmt == "one_word" and q.get("correct_answer"):
            answer_lines.append(f"**Q{i}.** {q['correct_answer']}")
            answer_lines.append(f"*{q.get('explanation', '')}*")
        elif q.get("expected_answer_summary"):
            answer_lines.append(f"**Q{i}.** {q['expected_answer_summary']}")
        else:
            # The model didn't populate the fields expected for the requested
            # format (an occasional LLM inconsistency even with a structured
            # schema, since nothing enforces "mcq requires options" at the
            # schema level — all Question fields are Optional so the same
            # model can serve all four formats). Surface whatever answer
            # content IS available instead of crashing the whole export.
            fallback_text = (
                q.get("explanation") or q.get("expected_answer_summary")
                or q.get("correct_answer") or "(No answer content was generated for this question.)"
            )
            print(f"Warning: Q{i} is missing the fields expected for format '{fmt}'; "
                  f"using fallback answer text instead of crashing.")
            answer_lines.append(f"**Q{i}.** {fallback_text}")
        answer_lines.append("")

    lines.extend(answer_lines)
    return "\n".join(lines)


# --- natural language request parsing ---

PARSE_REQUEST_SYSTEM = """Extract quiz generation parameters from the student's natural-language
request.

Guidance for mapping their words to fields:
- "numericals"/"calculations"/"problems with numbers" -> content_type "numerical"
- "derivations"/"derive"/"prove"/"show the steps for" -> content_type "derivation"
- "descriptive"/"explain in words"/"discuss"/"conceptual" -> content_type "descriptive"
- "theory"/"definitions"/"concepts" (or unspecified) -> content_type "theory"
- "multiple choice"/"mcq"/"options" (or unspecified) -> format "mcq"
- "one word"/"single word answer" -> format "one_word"
- "short answer"/"brief" -> format "short_answer"
- "long answer"/"detailed"/"full explanation"/"essay" -> format "long_answer"
- "all"/"every possible"/"as many as you can"/"exhaustive" -> count "all"
- "diagram"/"circuit diagram"/"figure"/"schematic"/"graph"/"chart"/"pie chart"/"plot"/
  "with a diagram"/"based on a circuit" -> needs_diagram true — ONLY when the user's own words
  explicitly use one of these terms. Do NOT infer needs_diagram from the topic simply being about
  circuits/electronics — e.g. "10 questions on Thevenin's theorem" is needs_diagram FALSE unless a
  diagram/chart/figure is explicitly requested in the text.
- If diagrams/charts/graphs aren't mentioned at all -> needs_diagram false
- If difficulty isn't mentioned, default to "medium". If format isn't mentioned, default to "mcq".
  If content_type isn't mentioned, default to "theory". If count isn't mentioned, default to 5.
"""

parse_request_prompt = ChatPromptTemplate.from_messages([
    ("system", PARSE_REQUEST_SYSTEM),
    ("human", "{user_text}"),
])

# Small classification-style task (extracting a QuizRequest from free text) —
# low reasoning effort is plenty and keeps this call fast.
_parse_llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    reasoning_effort="low",
)
parse_request_chain = parse_request_prompt | _parse_llm.with_structured_output(QuizRequest)


def parse_natural_language_request(user_text):
    request = parse_request_chain.invoke({"user_text": user_text})
    return request.model_dump()


def build_request_interactively():
    print("=== Quiz Generator (RAG-based, LangChain + Chroma) ===\n")
    print("Describe what you want in your own words, e.g.:")
    print('  "Give me 10 hard derivation questions on Thevenin and Norton theorems"')
    print('  "I want all numerical MCQs about circuit analysis, medium difficulty"')
    print('  "5 easy one-word questions about basic definitions"')
    print('  "3 medium numerical MCQs on Thevenin resistance with circuit diagrams"')
    print('  "5 MCQs on power distribution with a pie chart"\n')

    user_text = input("Your request: ").strip()

    print("\nInterpreting your request...")
    request = parse_natural_language_request(user_text)

    diagram_note = ", with diagrams/charts" if request.get("needs_diagram") else ""
    print(f"\nUnderstood as: {request['count']} {request['difficulty']} {request['content_type']} "
          f"{request['format']} question(s){diagram_note} on topic: {request['topic'] or '(broad search)'}\n")

    confirm = input("Proceed? (y/n) [y]: ").strip().lower()
    if confirm == "n":
        print("Let's try again.")
        return build_request_interactively()

    return request


if __name__ == "__main__":
    # Two ways to run:
    #   python generate_quiz.py                  -> interactive prompts
    #   python generate_quiz.py my_request.json   -> load from a saved JSON file
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            request = json.load(f)
    else:
        request = build_request_interactively()

    result = generate_question_set(request)

    with open("quiz.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    markdown_output = format_questions_as_markdown(result)
    with open("quiz.md", "w", encoding="utf-8") as f:
        f.write(markdown_output)

    print(f"\nGenerated {len(result['questions'])} questions, drawn from: "
          f"{', '.join(result['sources'])}")
    print("Saved to quiz.json (structured) and quiz.md (readable)")