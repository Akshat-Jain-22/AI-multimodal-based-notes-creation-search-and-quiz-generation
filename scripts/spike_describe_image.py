"""
spike_describe_image.py — Phase 0 spike: NOT part of the pipeline yet.

Standalone test to judge whether Groq's qwen/qwen3.6-27b vision model
produces good enough descriptions of circuit diagrams, graphs, and other
slide/screen-capture images to be worth building describe_images.py around.

Run this against 2-3 REAL images from your own lectures before we write any
pipeline code — specifically:
  - one circuit diagram
  - one graph/chart
  - one plain diagram or table

Usage:
    python spike_describe_image.py path/to/image.png [ocr_hint_text]

The optional ocr_hint mimics what chunk_lecture.py's collect_diagram_images()
already captures (the OCR text near that image) — passing it in lets us judge
whether combining "what OCR already read" + "what the VLM sees" produces a
meaningfully better description than either alone.
"""

import base64
import os
import sys

from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Preview-tier model — see the Phase 0 writeup for why this one over
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
as a hint, not ground truth): {ocr_hint}

Description:"""


def encode_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def describe_image(image_path, ocr_hint=""):
    ext = os.path.splitext(image_path)[1].lstrip(".").lower()
    media_type = "png" if ext == "png" else "jpeg"
    base64_image = encode_image(image_path)

    prompt = DESCRIBE_PROMPT_TEMPLATE.format(ocr_hint=ocr_hint.strip() or "(none captured)")

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
        # qwen3.6-27b defaults to a visible <think>...</think> reasoning trace
        # (thinking mode) — for a short factual caption there's no multi-step
        # logic to work through, so non-thinking mode is both cheaper (no
        # wasted reasoning tokens, which bill at this model's pricier output
        # rate) and avoids the trace silently consuming the whole token
        # budget before an actual answer is ever produced (see the first
        # spike run — it got cut off entirely mid-<think> at 300 tokens).
        reasoning_effort="none",
    )
    return completion.choices[0].message.content.strip()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python spike_describe_image.py <image_path> [ocr_hint_text]", file=sys.stderr)
        sys.exit(1)

    image_path = sys.argv[1]
    ocr_hint = sys.argv[2] if len(sys.argv) > 2 else ""

    if not os.path.exists(image_path):
        print(f"Error: file not found: {image_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Describing {image_path} with model {VISION_MODEL}...\n")
    description = describe_image(image_path, ocr_hint)
    print("--- Description ---")
    print(description)