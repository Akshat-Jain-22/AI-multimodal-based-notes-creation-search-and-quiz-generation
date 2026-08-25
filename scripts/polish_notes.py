import sys
import os
import re
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


POLISH_PROMPT_TEMPLATE = """You are editing a set of auto-generated lecture notes to make them read like a
polished, coherent textbook chapter — without changing any factual content.

The notes below were generated section-by-section from different parts of the same lecture, so they
may have: repeated or overlapping headings, abrupt transitions between sections, overly choppy/bulleted
prose that doesn't flow naturally, and inconsistently formatted mathematical equations.

Your task — rewrite the ENTIRE document below with these improvements:

1. Add a brief 2-3 sentence introduction at the very top (after the main title) summarizing what the
   lecture covers overall.
2. Merge or rename duplicate/overlapping section headings so the document reads as one coherent set
   of notes, not disconnected fragments. Reorganize section order only if needed for logical flow —
   do not remove any factual content while doing this.
3. Improve prose quality throughout: favor connected, natural explanatory sentences over disconnected
   bullet points. Keep bullets only where they genuinely represent a list (steps, distinct properties,
   parallel examples) — convert bullet-heavy sections that are really just explanations in disguise
   into flowing paragraphs instead. The overall voice should read like a well-written textbook chapter,
   consistent from start to finish, not like a stitched-together transcript summary.
4. Reformat ALL mathematical equations and formulas using LaTeX notation:
   - Inline math: wrap in single dollar signs, e.g. $V = IR$
   - Standalone/important equations: wrap in double dollar signs on their own line, e.g. $$V_{{TH}} = \\frac{{R_L}}{{R_L + R_{{TH}}}} V_{{OC}}$$
   - Use proper subscripts (e.g. $R_{{TH}}$ not "R_Thevenin" or "RTH"), Greek letters where relevant
     (e.g. $\\Delta$ for delta), and fractions using \\frac{{}}{{}} instead of plain "/"
5. Add a brief closing summary (3-5 bullet points of key takeaways) at the very end — this is the one
   place bullets should dominate, since it's meant as a quick-reference recap.
6. Do NOT modify, remove, or move any lines that start with "![" (these are embedded images) —
   copy them EXACTLY as they appear, in their original position relative to the surrounding text.
7. Do NOT invent, remove, or alter any factual/technical content — this is a formatting, prose-quality,
   and structure pass only.

Notes to edit:

{full_notes}
"""


def polish_notes(notes_md_path, max_tokens=6000):
    with open(notes_md_path, "r", encoding="utf-8") as f:
        full_notes = f.read()

    prompt = POLISH_PROMPT_TEMPLATE.format(full_notes=full_notes)

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}]
    )

    polished = response.choices[0].message.content.strip()
    return polished


if __name__ == "__main__":
    input_path = sys.argv[1] if len(sys.argv) > 1 else "lecture_notes.md"
    output_path = sys.argv[2] if len(sys.argv) > 2 else "lecture_notes_polished.md"

    print("Polishing notes (this may take a moment for a full document)...")
    polished = polish_notes(input_path)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(polished)

    print(f"Polished notes saved to {output_path} ({len(polished)} chars)")
    print("\nNote: LaTeX math (e.g. $V_{TH}$) renders on GitHub automatically.")
    print("For local VS Code preview with math rendering, install the 'Markdown+Math' extension.")