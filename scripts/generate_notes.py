import json
import sys
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


NOTES_PROMPT_TEMPLATE = """You are an experienced teaching assistant writing study notes for students, in the
style of a well-written textbook section — not a generic AI summary.

The segment below contains a mix of SPOKEN content (what the teacher said) and ON SCREEN content
(text detected on slides/board, which may be imperfect due to OCR errors — use your judgment and
prioritize the SPOKEN content when they conflict or when screen text looks garbled).

CONTEXT (for continuity only — this was already covered in the previous section, do NOT create notes for it):
{context_text}

MAIN SEGMENT (create notes for this part only):
{chunk_text}

Writing style — follow this closely:
- Default to natural, flowing prose, the way a textbook explains a concept — connected sentences
  that build on each other, not a list of disconnected facts.
- Use bullet points ONLY for genuine lists: multi-step procedures, a set of distinct properties,
  or several parallel examples. Do NOT use bullets as a default way to present every fact — most
  explanations should read as prose.
- Write like you're teaching the concept to a student who wasn't in class, not like you're
  summarizing a transcript. Explain WHY something works, not just WHAT was said.
- Vary sentence structure and length naturally — avoid starting every sentence or bullet the same way.
- Use a consistent, confident, explanatory tone throughout — as if this is one coherent section of
  a textbook chapter, not a collection of notes stitched from fragments.

Content requirements:
- Start with a short, descriptive heading (##) summarizing the segment's main topic
- Include any specific examples, numbers, or formulas mentioned, exactly as stated, woven naturally
  into the explanation (not just listed)
- If the MAIN SEGMENT references or completes something from the CONTEXT (e.g., finishing a
  calculation that started earlier), use the CONTEXT to complete it correctly rather than leaving it unresolved
- Do NOT include timestamps, "SPOKEN:"/"ON SCREEN:" labels, or meta-commentary in your output
- Do NOT invent content that isn't supported by the segment or context below
"""


def generate_notes_for_chunk(chunk_text, context_text, chunk_number, retries=2):
    prompt = NOTES_PROMPT_TEMPLATE.format(
        chunk_text=chunk_text,
        context_text=context_text if context_text else "(no prior context — this is the first section)"
    )

    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                max_tokens=1500,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            if attempt < retries - 1:
                print(f"  Chunk {chunk_number}: error ({e}), retrying...")
                continue
            print(f"  Chunk {chunk_number}: failed after {retries} attempts — {e}")
            return f"*(Notes generation failed for this segment: {e})*"


def format_diagram_images_markdown(diagram_images):
    """Build a Markdown block embedding each likely-diagram image.

    Two-line format per image (this exact shape matters —
    chunk_notes_for_search.py's parse_diagram_paragraph() parses it):
      1. ![alt text](path) — kept SHORT and OCR-snippet-based, since this
         becomes the real HTML alt attribute when notes render in the
         frontend (MathMarkdown/react-markdown), not a place for a full
         paragraph.
      2. *caption* — the full sentence-level description from
         describe_images.py when available (chunk_lecture.py's
         build_chunks() already calls describe_diagram_images() on every
         diagram candidate before notes generation ever sees it), falling
         back to the same short text used for the alt attribute if a
         description wasn't produced for some reason.

    NOTE: chunk_notes_for_search.py currently only extracts the alt text
    (line 1) into its diagram_images metadata for indexing — the richer
    description on line 2 isn't folded into searchable passage text yet.
    That's a separate, still-open change, not done here.
    """
    if not diagram_images:
        return ""

    lines = ["**Diagrams/board content from this segment:**", ""]
    for img in diagram_images:
        path = img["image_file"].replace("\\", "/")
        ocr_hint = (img.get("ocr_text") or "").strip()
        description = (img.get("description") or "").strip()

        if ocr_hint:
            # Short snippet of the OCR text as the alt text, falling back
            # to the timestamp if it's empty/unhelpful.
            snippet = " ".join(ocr_hint.split())[:60]
            alt_text = f"{snippet} (captured at {img['timestamp']:.1f}s)"
        else:
            alt_text = f"Captured at {img['timestamp']:.1f}s"

        caption = description if description else alt_text

        lines.append(f"![{alt_text}]({path})")
        lines.append(f"*{caption}*")
        lines.append("")

    return "\n".join(lines)


def generate_full_notes(chunks_path, lecture_title="Lecture Notes"):
    with open(chunks_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    notes_sections = []
    for chunk in chunks:
        print(f"Generating notes for chunk {chunk['chunk_number']} "
              f"({chunk['start_time']}s - {chunk['end_time']}s)...")
        notes = generate_notes_for_chunk(
            chunk["text"], chunk.get("context_text", ""), chunk["chunk_number"]
        )

        diagram_block = format_diagram_images_markdown(chunk.get("diagram_images", []))
        if diagram_block:
            notes = notes + "\n\n" + diagram_block

        notes_sections.append(notes)

    full_notes = f"# {lecture_title}\n\n" + "\n\n---\n\n".join(notes_sections)
    return full_notes


if __name__ == "__main__":
    chunks_path = sys.argv[1] if len(sys.argv) > 1 else "lecture_chunks.json"
    lecture_title = sys.argv[2] if len(sys.argv) > 2 else "Lecture Notes"

    full_notes = generate_full_notes(chunks_path, lecture_title)

    with open("lecture_notes.md", "w", encoding="utf-8") as f:
        f.write(full_notes)

    print(f"\nGenerated notes saved to lecture_notes.md ({len(full_notes)} chars)")