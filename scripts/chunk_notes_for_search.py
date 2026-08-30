import json
import sys
import re
import os


def slugify(text, max_length=50):
    """Turn a lecture title into a stable, id-safe slug.

    Deterministic (same title always -> same slug), which matters because
    build_search_index.py relies on stable passage ids to safely skip
    already-indexed passages on re-runs.
    """
    slug = text.lower()
    slug = re.sub(r"[^a-z0-9]+", "_", slug).strip("_")
    return slug[:max_length] or "lecture"


IMAGE_LINE_RE = re.compile(r"^!\[(.*?)\]\((.*?)\)")


def parse_diagram_paragraph(para):
    """If a paragraph is an embedded diagram image block (as written by
    generate_notes.py's format_diagram_images_markdown — an image line
    followed by an italic caption line), extract its caption and image path.
    Returns None if this paragraph isn't an image block."""
    first_line = para.strip().split("\n", 1)[0].strip()
    m = IMAGE_LINE_RE.match(first_line)
    if not m:
        return None
    return {"caption": m.group(1), "image_file": m.group(2)}


def split_into_passages(section_heading, body_text, max_words=250):
    """Split one section's body text into passages of roughly max_words each,
    breaking on paragraph boundaries so we don't cut a sentence in half.

    Embedded diagram images are pulled OUT of the running text (so raw
    Markdown/paths don't pollute the embedding vector or the LLM context) but
    are preserved as structured metadata attached to whichever passage they
    fell within. Previously these were silently discarded entirely, which
    meant quiz/search features had zero awareness that a diagram existed —
    this is what's fixed here.

    Returns a list of dicts: {"text": str, "diagram_images": [ {caption, image_file}, ... ]}
    """
    paragraphs = [p.strip() for p in body_text.split("\n\n") if p.strip()]

    passages = []
    current_words = []
    current_count = 0
    current_diagrams = []

    def flush():
        if current_words or current_diagrams:
            passages.append({
                "text": " ".join(current_words),
                "diagram_images": current_diagrams[:]
            })

    for para in paragraphs:
        diagram = parse_diagram_paragraph(para)
        if diagram:
            current_diagrams.append(diagram)
            continue

        para_word_count = len(para.split())

        if current_count + para_word_count > max_words and current_words:
            flush()
            current_words = []
            current_count = 0
            current_diagrams = []

        current_words.append(para)
        current_count += para_word_count

    flush()

    return passages


def extract_sections(notes_content):
    parts = re.split(r"^##\s+(.+)$", notes_content, flags=re.MULTILINE)
    sections = []
    for i in range(1, len(parts), 2):
        heading = parts[i].strip()
        body = parts[i + 1].strip() if i + 1 < len(parts) else ""
        sections.append((heading, body))
    return sections


def chunk_notes_for_search(notes_md_path, lecture_id=None, lecture_title=None, max_words=250):
    with open(notes_md_path, "r", encoding="utf-8") as f:
        notes_content = f.read()

    if lecture_title is None:
        title_match = re.match(r"^#\s+(.+)$", notes_content, flags=re.MULTILINE)
        lecture_title = (
            title_match.group(1).strip()
            if title_match
            else os.path.splitext(os.path.basename(notes_md_path))[0]
        )

    if lecture_id is None:
        lecture_id = slugify(lecture_title)

    sections = extract_sections(notes_content)

    search_passages = []
    for heading, body in sections:
        if heading.strip().lower() in ("key takeaways",):
            continue

        passages = split_into_passages(heading, body, max_words)
        for i, passage in enumerate(passages):
            search_passages.append({
                "id": f"{lecture_id}::{heading}::{i}",
                "lecture_id": lecture_id,
                "lecture_title": lecture_title,
                "section_heading": heading,
                "text": passage["text"],
                "diagram_images": passage["diagram_images"]
            })

    return search_passages


if __name__ == "__main__":
    notes_path = sys.argv[1] if len(sys.argv) > 1 else "lecture_notes_polished.md"
    lecture_id = sys.argv[2] if len(sys.argv) > 2 else None

    passages = chunk_notes_for_search(notes_path, lecture_id=lecture_id)

    with open("search_passages.json", "w", encoding="utf-8") as f:
        json.dump(passages, f, indent=2, ensure_ascii=False)

    total_diagrams = sum(len(p["diagram_images"]) for p in passages)
    print(f"Split into {len(passages)} search passages ({total_diagrams} diagram image(s) captured):")
    for p in passages:
        diagram_note = f", {len(p['diagram_images'])} diagram(s)" if p["diagram_images"] else ""
        print(f"  [{p['section_heading']}] ({len(p['text'].split())} words{diagram_note})")
    print(f"lecture_id: {passages[0]['lecture_id'] if passages else '(none)'}")
    print("Saved to search_passages.json")