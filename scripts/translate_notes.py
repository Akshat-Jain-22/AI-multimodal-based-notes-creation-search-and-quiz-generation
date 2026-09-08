"""
translate_notes.py — translates a lecture's polished notes into a target
language, on demand. The caching (checking/writing lecture_translations rows
in db.py) lives in api.py's endpoint, not here — this module is just the
pure translation step, same separation of concerns as polish_notes.py /
translate_transcript.py.

Two things in the notes MUST survive translation completely unchanged:
  - embedded diagram image lines, e.g. ![caption](path/to/image.png)
  - LaTeX math, both inline ($V = IR$) and block ($$...$$)

Rather than just instructing the LLM not to touch these (fragile — the same
class of instruction-following slip generate_notes.py/polish_notes.py deal
with elsewhere in this project, e.g. MathMarkdown.jsx's delimiter-drift
workaround), this module extracts them into placeholder tokens BEFORE
sending text to the LLM, and restores the original text after — the model
never sees the real LaTeX/image markup, so there's nothing for it to
mistranslate, reformat, or drop.

Chunking: same idea as generate_notes.py/chunk_notes_for_search.py — split on
"## " section boundaries so a full lecture's notes don't blow the model's
context/output budget in one call, and so a failure on one section doesn't
lose the whole document (degrades to untranslated original text for just
that section, same fallback pattern as generate_notes.py).
"""

import os
import re
import sys
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# ---------------------------------------------------------------------------
# Language code -> display name. users.preferred_language stores short codes
# (matches what a frontend <select> would send, e.g. 'hi'), but the LLM
# translates more reliably and unambiguously when given a plain language
# name in the prompt rather than a bare code (e.g. "hi" alone risks being
# read as the greeting, not the code for Hindi). Unrecognized codes are
# passed through as-is, so this list doesn't need to be exhaustive to be
# useful — it's a readability aid for the prompt, not a validation gate.
# ---------------------------------------------------------------------------

LANGUAGE_NAMES = {
    "en": "English",
    # The 22 languages listed in the Eighth Schedule of the Indian
    # Constitution. Six of these (Bodo, Dogri, Konkani, Maithili, Manipuri,
    # Santali) don't have two-letter ISO 639-1 codes, only three-letter
    # ISO 639-2/3 codes — used here since nothing in this system requires a
    # two-letter code, these are just internal identifiers (see db.py's
    # users.preferred_language and LanguageSelect.jsx's SUPPORTED_LANGUAGES,
    # which must stay in sync with this dict).
    "as": "Assamese",
    "bn": "Bengali",
    "brx": "Bodo",
    "doi": "Dogri",
    "gu": "Gujarati",
    "hi": "Hindi",
    "kn": "Kannada",
    "ks": "Kashmiri",
    "kok": "Konkani",
    "mai": "Maithili",
    "ml": "Malayalam",
    "mni": "Manipuri (Meitei)",
    "mr": "Marathi",
    "ne": "Nepali",
    "or": "Odia",
    "pa": "Punjabi",
    "sa": "Sanskrit",
    "sat": "Santali",
    "sd": "Sindhi",
    "ta": "Tamil",
    "te": "Telugu",
    "ur": "Urdu",
}


def resolve_language_name(language_code_or_name):
    key = (language_code_or_name or "").strip().lower()
    return LANGUAGE_NAMES.get(key, language_code_or_name)


# ---------------------------------------------------------------------------
# Placeholder protection for content that must survive translation verbatim
# ---------------------------------------------------------------------------

# Order matters: block math ($$...$$) must be matched before inline math
# ($...$), otherwise the inline pattern could match into a block math span
# first and split it incorrectly.
IMAGE_LINE_RE = re.compile(r"^!\[.*?\]\(.*?\)\s*$", re.MULTILINE)
BLOCK_MATH_RE = re.compile(r"\$\$.+?\$\$", re.DOTALL)
INLINE_MATH_RE = re.compile(r"\$[^\$\n]+?\$")

# Deliberately not a plain-ASCII word like "TOKEN0" — that's exactly the
# kind of string a translation model might "helpfully" translate, reformat,
# or mangle spacing/punctuation around. This bracket+digit shape is unlikely
# to occur naturally in any language and unlikely to be touched by a
# translation task that's told explicitly to leave it alone.
PLACEHOLDER_TEMPLATE = "\u27e6PROTECT{}\u27e7"
PLACEHOLDER_RE = re.compile(r"\u27e6PROTECT(\d+)\u27e7")


def _protect(text):
    """Replace image lines and LaTeX math with placeholder tokens. Returns
    (masked_text, protected_list) where protected_list[i] is the original
    string for placeholder index i."""
    protected = []

    def _stash(match):
        idx = len(protected)
        protected.append(match.group(0))
        return PLACEHOLDER_TEMPLATE.format(idx)

    text = IMAGE_LINE_RE.sub(_stash, text)
    text = BLOCK_MATH_RE.sub(_stash, text)
    text = INLINE_MATH_RE.sub(_stash, text)
    return text, protected


def _restore(text, protected):
    def _unstash(match):
        idx = int(match.group(1))
        if idx < len(protected):
            return protected[idx]
        # The model dropped or duplicated a placeholder — leave whatever it
        # wrote rather than crashing the whole translation over one lost
        # image/formula. Rare, worth flagging, not fatal.
        print(f"Warning: placeholder {match.group(0)} has no matching protected span — left as-is.")
        return match.group(0)

    return PLACEHOLDER_RE.sub(_unstash, text)


# ---------------------------------------------------------------------------
# Chunking — split on "## " section boundaries, keeping the title/intro
# (everything before the first "## ") as its own leading chunk. Chunks
# concatenate back to the original document exactly.
# ---------------------------------------------------------------------------

def _split_into_chunks(markdown_text):
    match_positions = [m.start() for m in re.finditer(r"^## ", markdown_text, flags=re.MULTILINE)]

    if not match_positions:
        return [markdown_text]

    chunks = []
    if match_positions[0] > 0:
        chunks.append(markdown_text[:match_positions[0]])

    for i, start in enumerate(match_positions):
        end = match_positions[i + 1] if i + 1 < len(match_positions) else len(markdown_text)
        chunks.append(markdown_text[start:end])

    return chunks


# ---------------------------------------------------------------------------
# Translation
# ---------------------------------------------------------------------------

TRANSLATE_PROMPT_TEMPLATE = """Translate the following lecture-notes excerpt (Markdown format) into {language}.

Rules:
- Translate ALL prose, headings, and bullet text into {language}.
- Do NOT translate, remove, reorder, or alter tokens that look like \u27e6PROTECT0\u27e7, \u27e6PROTECT1\u27e7,
  etc. Copy each one EXACTLY as it appears, in the same position — these are placeholders for
  content that must remain unchanged (images and formulas).
- Preserve all Markdown formatting exactly: heading levels (##), bullet points (-), bold (**),
  and blank lines between paragraphs.
- Do NOT add commentary, notes, or explanations of your own — output ONLY the translated Markdown.
- Keep standalone technical abbreviations, proper nouns, or variable-style names (e.g. R_TH, V_OC)
  as-is if translating them would be unnatural or ambiguous in {language}.

Excerpt:
{chunk_text}
"""


def _translate_chunk(chunk_text, language_name, retries=2):
    # Chunks are reassembled with plain string concatenation (_split_into_
    # chunks guarantees "".join(chunks) == original), so the blank-line
    # separator between one section and the next lives in this chunk's own
    # leading/trailing whitespace. LLMs routinely trim trailing blank lines
    # from their output even when told not to — left unguarded, that would
    # glue "...end of section.## Next Heading" together with the "##" no
    # longer at the start of a line, silently breaking Markdown heading
    # parsing downstream. Stripping the whitespace off BEFORE the API call
    # and splicing the ORIGINAL whitespace back on afterward makes section
    # spacing immune to whatever the model does with its own output.
    leading_len = len(chunk_text) - len(chunk_text.lstrip())
    trailing_len = len(chunk_text) - len(chunk_text.rstrip())
    leading_ws = chunk_text[:leading_len]
    trailing_ws = chunk_text[len(chunk_text) - trailing_len:] if trailing_len else ""
    core_text = chunk_text[leading_len: len(chunk_text) - trailing_len] if trailing_len else chunk_text[leading_len:]

    if not core_text.strip():
        # Nothing but whitespace in this chunk — nothing to translate.
        return chunk_text

    masked_text, protected = _protect(core_text)

    if not masked_text.strip():
        # Core is entirely protected content (e.g. a lone image line) —
        # skip the API call, there's no prose here to translate.
        return leading_ws + _restore(masked_text, protected) + trailing_ws

    prompt = TRANSLATE_PROMPT_TEMPLATE.format(language=language_name, chunk_text=masked_text)

    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            translated_masked = response.choices[0].message.content.strip()
            return leading_ws + _restore(translated_masked, protected) + trailing_ws
        except Exception as e:
            if attempt < retries - 1:
                print(f"  Translation chunk failed ({e}), retrying...")
                continue
            print(f"  Translation chunk failed after {retries} attempts ({e}) — "
                  f"keeping original (untranslated) text for this section.")
            return chunk_text


def translate_notes(notes_md_path, language):
    """Translates a full notes Markdown file into `language` (an ISO-ish
    code like 'hi', or a plain name like 'Hindi' — either works, resolved
    via resolve_language_name()). Returns the translated Markdown as a
    string. Degrades gracefully per-chunk on failure (same pattern as
    generate_notes.py) — a single failed section falls back to its
    original, untranslated text rather than losing the whole document."""
    language_name = resolve_language_name(language)

    with open(notes_md_path, "r", encoding="utf-8") as f:
        full_notes = f.read()

    chunks = _split_into_chunks(full_notes)
    print(f"Translating {len(chunks)} section(s) into {language_name}...")

    translated_chunks = []
    for i, chunk in enumerate(chunks, start=1):
        print(f"  [{i}/{len(chunks)}]...")
        translated_chunks.append(_translate_chunk(chunk, language_name))

    return "".join(translated_chunks)


if __name__ == "__main__":
    input_path = sys.argv[1] if len(sys.argv) > 1 else "lecture_notes_polished.md"
    language = sys.argv[2] if len(sys.argv) > 2 else "hi"
    output_path = sys.argv[3] if len(sys.argv) > 3 else input_path.replace(".md", f"_{language.lower()}.md")

    translated = translate_notes(input_path, language)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(translated)

    print(f"\nTranslated notes saved to {output_path} ({len(translated)} chars)")