import json
import sys
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def translate_transcript(transcript_json_path):
    with open(transcript_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    segments = data["segments"]

    numbered_lines = []
    for i, seg in enumerate(segments):
        numbered_lines.append(f"{i+1}. {seg['text']}")
    numbered_text = "\n".join(numbered_lines)

    prompt = f"""Translate the following numbered lecture transcript lines into clear, natural English.
Maintain consistent terminology throughout — if a word/concept appears in multiple lines, translate it the SAME way every time.
Do not merge, split, add, or remove lines — return exactly the same number of lines, in the same order, each starting with its original number and a period.
Do not add commentary or explanation.

Source language: {data.get('source_language', 'unknown')}

Transcript lines:
{numbered_text}"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )

    translated_raw = response.choices[0].message.content.strip()

    translated_lines = {}
    for line in translated_raw.split("\n"):
        line = line.strip()
        if not line:
            continue

        if "." in line:
            num_part, _, text_part = line.partition(".")
            num_part = num_part.strip()
            if num_part.isdigit():
                translated_lines[int(num_part)] = text_part.strip()

    translated_segments = []
    for i, seg in enumerate(segments):
        translated_text = translated_lines.get(i + 1, seg["text"])  # fallback to original if parsing missed a line
        translated_segments.append({
            "start": seg["start"],
            "end": seg["end"],
            "original_text": seg["text"],
            "translated_text": translated_text
        })

    output = {
        "source_language": data.get("source_language"),
        "segments": translated_segments
    }

    output_path = transcript_json_path.replace(".json", "_translated.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Translated {len(translated_segments)} segments (with timestamps preserved).")
    print(f"Saved to {output_path}")


if __name__ == "__main__":
    input_file = sys.argv[1] if len(sys.argv) > 1 else "audio_transcript.json"
    translate_transcript(input_file)