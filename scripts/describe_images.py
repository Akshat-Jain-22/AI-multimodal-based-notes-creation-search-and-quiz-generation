"""
describe_images.py — generates accurate, searchable text descriptions of
diagram images (circuits, graphs, charts, other visual content) captured
from lecture slides/screen recordings, using Groq's qwen/qwen3.6-27b vision
model.

Two hard constraints came directly out of a Phase 0 spike against a real
lecture slide (see project notes) and are baked into this module as CODE,
not just documentation, since both were the difference between a fluent-but-
wrong answer and a correct one:

1. reasoning_effort="none" is REQUIRED. qwen3.6-27b defaults to a visible
   <think>...</think> reasoning trace (thinking mode). Left on, it silently
   ate the ENTIRE token budget reasoning about one circuit image and never
   produced an answer at all — and even when given enough budget to finish,
   thinking mode bills extra output tokens (this model's pricier direction)
   for reasoning a short factual caption doesn't need.

2. The OCR hint is NOT optional enrichment — it's load-bearing for
   correctness. Tested directly, same image, same model, same prompt:
   WITHOUT the hint, the model confidently mislabeled a load resistor as
   "R_4" — a component that doesn't exist in that circuit. WITH the exact
   same OCR text passed in, it read every label correctly, including R_L.
   A fluent, confident, wrong caption is worse than no caption, because
   nothing about the output looks broken — it would have silently
   propagated into notes, search, and quiz content. describe_image() below
   takes ocr_hint as a REQUIRED parameter (no default) specifically so a
   call site can't accidentally skip it; pass "" explicitly if an image
   genuinely has no nearby OCR text, rather than omitting the argument.
"""

import base64
import os
import sys

from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Preview-tier model on Groq — see project notes for why this one over
# qwen3.8-27b. Kept as a single constant so it's a one-line swap if Groq
# deprecates it or a better option shows up later.
VISION_MODEL = "qwen/qwen3.6-27b"

DESCRIBE_PROMPT_TEMPLATE = """This image was captured from a lecture slide or screen recording. Describe
what it shows in 2-4 sentences, precisely enough that a student could find this content by
searching for it and a quiz could ask a question about it.

- If it's a circuit diagram: describe the topology (series/parallel), every component with its
  exact labeled value (resistors, sources, etc.), and what's being asked for or shown, if evident.
- If it's a graph or chart: describe the axes (with units if labeled), the type of plot, and the
  overall shape/trend of what's plotted (e.g. "rises linearly then plateaus", "three bars showing
  decreasing values").
- If it's a plain diagram or illustration: describe the key labeled parts and what concept it's
  illustrating.
- If it's mostly just text (a slide that isn't really a diagram): say so plainly instead of
  inventing visual detail that isn't there.

Nearby OCR text already extracted from this slide (may be incomplete or slightly garbled — use it
as a hint, not ground truth, but trust it over your own guess for any label it clearly contains):
{ocr_hint}

Description:"""


def _encode_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def _media_type_for(image_path):
    ext = os.path.splitext(image_path)[1].lstrip(".").lower()
    return "png" if ext == "png" else "jpeg"


def describe_image(image_path, ocr_hint, retries=2):
    """Returns a text description of the image at image_path, grounded by
    ocr_hint (see module docstring — this argument is required on purpose).

    Degrades gracefully on failure (same pattern as generate_notes.py /
    translate_notes.py elsewhere in this project): falls back to the raw
    OCR text if the vision call fails after retries, rather than losing the
    image's textual representation entirely, or crashing the whole notes
    generation over one bad image.
    """
    if not ocr_hint or not ocr_hint.strip():
        print(f"Warning: describing {image_path} with NO OCR hint — label accuracy "
              f"(component names, axis text, etc.) is less reliable without one. "
              f"Confirm this image genuinely has no nearby OCR text before trusting "
              f"this description at face value.")

    base64_image = _encode_image(image_path)
    media_type = _media_type_for(image_path)
    prompt = DESCRIBE_PROMPT_TEMPLATE.format(ocr_hint=ocr_hint.strip() or "(none captured)")

    for attempt in range(retries):
        try:
            completion = client.chat.completions.create(
                model=VISION_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/{media_type};base64,{base64_image}"},
                            },
                        ],
                    }
                ],
                temperature=0.3,
                max_completion_tokens=500,
                reasoning_effort="none",  # see module docstring, constraint 1
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            if attempt < retries - 1:
                print(f"  Image description failed for {image_path} ({e}), retrying...")
                continue
            print(f"  Image description failed for {image_path} after {retries} attempts "
                  f"({e}) — falling back to raw OCR text for this image.")
            return ocr_hint.strip() or "(no description available for this image)"


def describe_diagram_images(diagram_images):
    """Batch entry point matching the shape chunk_lecture.py's
    collect_diagram_images() already produces: a list of
    {"timestamp", "image_file", "ocr_text"} dicts. Returns the same list
    with a "description" key added to each entry — this is the direct
    wiring point for generate_notes.py (richer captions) and
    chunk_notes_for_search.py (making diagram content actually searchable),
    so both consume one enriched structure instead of duplicating the
    describe_image() call.
    """
    enriched = []
    for img in diagram_images:
        description = describe_image(img["image_file"], img.get("ocr_text", ""))
        enriched.append({**img, "description": description})
    return enriched


if __name__ == "__main__":
    # Usage: python describe_images.py <image_path> [ocr_hint_text]
    if len(sys.argv) < 2:
        print("Usage: python describe_images.py <image_path> [ocr_hint_text]", file=sys.stderr)
        sys.exit(1)

    image_path = sys.argv[1]
    ocr_hint = sys.argv[2] if len(sys.argv) > 2 else ""

    if not os.path.exists(image_path):
        print(f"Error: file not found: {image_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Describing {image_path} with model {VISION_MODEL}...\n")
    print(describe_image(image_path, ocr_hint))
