import json
import sys
import os
import re
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def build_word_timeline(segments):
    """
    Break each segment's text into words, and assign each word an estimated
    timestamp by evenly spacing words across the segment's start/end time.
    This gives us a rough per-word timeline we can use to re-timestamp
    sentences after we re-split them.
    """
    timeline = []
    for seg in segments:
        words = seg["text"].strip().split()
        if not words:
            continue
        duration = seg["end"] - seg["start"]
        step = duration / len(words) if len(words) > 0 else 0
        for i, word in enumerate(words):
            timeline.append({
                "word": word,
                "time": round(seg["start"] + i * step, 2)
            })
    return timeline


def join_and_resplit_sentences(segments):
    """
    Join all segment text into one continuous string, then split it into
    proper sentences using punctuation. Returns a list of sentences, each
    with an estimated start time (taken from the first word of that sentence).
    """
    timeline = build_word_timeline(segments)
    full_text = " ".join(item["word"] for item in timeline)

    raw_sentences = re.split(r'(?<=[.!?])\s+', full_text.strip())

    sentences_with_time = []
    word_pointer = 0

    for sentence in raw_sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        word_count = len(sentence.split())

        start_time = timeline[word_pointer]["time"] if word_pointer < len(timeline) else None

        sentences_with_time.append({
            "text": sentence,
            "start": start_time
        })

        word_pointer += word_count

    return sentences_with_time


def correct_transcript(transcript_json_path):
    with open(transcript_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    segments = data["segments"]

    sentences = join_and_resplit_sentences(segments)

    corrected_sentences = []

    for i, sentence_obj in enumerate(sentences):
        original_text = sentence_obj["text"]

        prev_text = sentences[i - 1]["text"] if i > 0 else ""
        next_text = sentences[i + 1]["text"] if i < len(sentences) - 1 else ""

        prompt = f"""This is a speech-to-text transcript sentence in {data.get('source_language', 'the original language')} that may contain words misheard due to acoustic similarity.

Use the surrounding context to correct only the TARGET sentence. Do NOT change sentence structure or meaning beyond fixing clear mishearing errors. Keep the correction in the SAME language as the original — do not translate. If nothing is wrong, return it unchanged.

Previous sentence (context only, do not return this): {prev_text}
TARGET sentence (correct and return only this): {original_text}
Next sentence (context only, do not return this): {next_text}

Return ONLY the corrected TARGET sentence text, nothing else."""

        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}]
        )

        corrected_text = response.choices[0].message.content.strip()

        corrected_sentences.append({
            "start": sentence_obj["start"],
            "original_text": original_text,
            "corrected_text": corrected_text
        })

        if corrected_text != original_text:
            print(f"[{sentence_obj['start']}s] CHANGED:\n  before: {original_text}\n  after:  {corrected_text}\n")

    output_data = {
        "source_language": data.get("source_language"),
        "language_confidence": data.get("language_confidence"),
        "sentences": corrected_sentences
    }

    output_path = transcript_json_path.replace(".json", "_corrected.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"\nSaved corrected transcript to {output_path}")


if __name__ == "__main__":
    input_file = sys.argv[1] if len(sys.argv) > 1 else "audio_transcript.json"
    correct_transcript(input_file)