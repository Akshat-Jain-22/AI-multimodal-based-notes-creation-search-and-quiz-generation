from faster_whisper import WhisperModel
import json
import sys

def transcribe_audio(audio_path, model_size="small", vocab_hint="", force_language=None, task="transcribe"):
    model = WhisperModel(model_size, device="cpu", compute_type="int8")

    segments, info = model.transcribe(
        audio_path,
        beam_size=5,
        language=force_language,
        task=task,  
        initial_prompt=vocab_hint if vocab_hint else None
    )

    print(f"Detected language: {info.language} (confidence: {info.language_probability:.2f})")

    transcript = []
    for segment in segments:
        transcript.append({
            "start": round(segment.start, 2),
            "end": round(segment.end, 2),
            "text": segment.text.strip()
        })
        print(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}")

    output = {
        "source_language": info.language,
        "language_confidence": info.language_probability,
        "task": task,
        "segments": transcript
    }

    return output

if __name__ == "__main__":
    audio_file = sys.argv[1] if len(sys.argv) > 1 else "sample_lecture.mp3"
    vocab_hint = sys.argv[2] if len(sys.argv) > 2 else ""
    force_language = sys.argv[3] if len(sys.argv) > 3 else None

    result = transcribe_audio(audio_file, vocab_hint=vocab_hint, force_language=force_language, task="translate")

    with open("audio_transcript.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\nSaved {len(result['segments'])} segments to audio_transcript.json")