"""
run_pipeline.py — end-to-end orchestrator for the notes-creation pipeline.

Takes raw lecture inputs (audio and/or screen recording, optionally a PPTX)
and drives every existing stage in order, ending with a lecture that's fully
indexed and ready for search_notes.py / generate_quiz.py. Every stage is
still its own independently-testable module — this file only sequences them
and handles the file-path handoffs between them.

    transcribe (native) -> [correct -> translate]  (skipped if already English)
    screen capture (OCR)                                 |
    pptx extraction (supplementary)                       v
                    \\                                fuse -> chunk -> notes
                     \\                                 -> polish -> chunk-for-
                      \\----------------------------------> search -> index

--- Adapter note ---
correct_transcript.py writes {"sentences": [{"start","original_text",
"corrected_text"}]}. translate_transcript.py expects {"segments":
[{"start","end","text"}]}. These don't match (different top-level key,
missing "end", "corrected_text" vs "text") — you can't literally pipe one
into the other. adapt_corrected_to_segments() below bridges that gap. It
synthesizes each sentence's "end" as the next sentence's "start" (or
+default_gap for the last sentence), since correct_transcript.py's sentence
re-split doesn't track true end times. translate_transcript.py only carries
"end" through to its own output without using it for anything internally,
so this approximation is safe for the pipeline as it exists today — but
flag it if you later add a stage that relies on accurate segment "end"
times for corrected/translated audio.
"""

import argparse
import json
import os
import re
import sys

from audio_to_text import transcribe_audio
from correct_transcript import correct_transcript
from translate_transcript import translate_transcript
from screen_to_text import extract_screen_content
from pptx_to_text import extract_pptx_content
from fuse import fuse_lecture_data
from chunk_lecture import build_chunks
from generate_notes import generate_full_notes
from polish_notes import polish_notes
from chunk_notes_for_search import chunk_notes_for_search
from build_search_index import build_index, PERSIST_DIR


def _safe_dirname(text, max_length=60):
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", text).strip("_").lower()
    return (slug[:max_length] or "lecture")


def _write_json(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return path


def adapt_corrected_to_segments(corrected_path, segments_path, default_gap=3.0):
    """Bridge correct_transcript.py's output schema into what
    translate_transcript.py expects as input. See module docstring."""
    with open(corrected_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    sentences = data.get("sentences", [])
    segments = []
    for i, s in enumerate(sentences):
        start = s.get("start")
        if i + 1 < len(sentences):
            end = sentences[i + 1].get("start")
        else:
            end = (start + default_gap) if start is not None else None

        segments.append({
            "start": start,
            "end": end,
            "text": s.get("corrected_text", s.get("original_text", "")),
        })

    out = {
        "source_language": data.get("source_language"),
        "language_confidence": data.get("language_confidence"),
        "segments": segments,
    }
    return _write_json(out, segments_path)


def process_audio(audio_path, work_dir, vocab_hint="", force_language=None,
                   model_size="small", skip_correction_for_english=True):
    """Transcribe natively, then correct + translate unless the detected
    language is already English (in which case correction/translation would
    be redundant — correct_transcript.py's job is fixing mishearing errors
    in the ORIGINAL language, and there's nothing to translate)."""
    print("\n[1/8] Transcribing audio (native language)...")
    native_path = os.path.join(work_dir, "audio_transcript_native.json")
    transcript = transcribe_audio(
        audio_path, model_size=model_size, vocab_hint=vocab_hint,
        force_language=force_language, task="transcribe"
    )
    _write_json(transcript, native_path)
    detected_lang = transcript.get("source_language")
    print(f"  Detected language: {detected_lang}")

    if skip_correction_for_english and detected_lang == "en":
        print("  Already English — skipping correction/translation stages.")
        return native_path

    print("[2/8] Correcting mishearing errors (native language)...")
    correct_transcript(native_path)
    corrected_path = native_path.replace(".json", "_corrected.json")

    print("[3/8] Adapting corrected transcript for translation stage...")
    segments_for_translation = os.path.join(work_dir, "audio_transcript_for_translation.json")
    adapt_corrected_to_segments(corrected_path, segments_for_translation)

    print("[4/8] Translating to English...")
    translate_transcript(segments_for_translation)
    translated_path = segments_for_translation.replace(".json", "_translated.json")

    return translated_path


def run_pipeline(lecture_title, audio_path=None, video_path=None, pptx_path=None,
                  vocab_hint="", force_language=None, model_size="small",
                  work_dir_root="pipeline_runs", chunk_duration_sec=360, overlap_sec=45,
                  chroma_persist_dir=PERSIST_DIR):
    if not audio_path and not video_path:
        raise ValueError(
            "Need at least an audio_path or video_path (fuse.py can't build a "
            "timeline from a PPTX alone — same constraint as the standalone scripts)."
        )

    work_dir = os.path.join(work_dir_root, _safe_dirname(lecture_title))
    os.makedirs(work_dir, exist_ok=True)
    print(f"=== Pipeline run: '{lecture_title}' ===")
    print(f"Working directory: {work_dir}")

    audio_data_path = None
    if audio_path:
        audio_data_path = process_audio(
            audio_path, work_dir, vocab_hint=vocab_hint,
            force_language=force_language, model_size=model_size
        )

    screen_data_path = None
    if video_path:
        print("\n[5/8] Extracting screen content (OCR + frame capture)...")
        screen_result = extract_screen_content(video_path)
        screen_data_path = _write_json(screen_result, os.path.join(work_dir, "screen_content.json"))

    pptx_data_path = None
    if pptx_path:
        print("\n[supplementary] Extracting PPTX content...")
        pptx_result = extract_pptx_content(pptx_path)
        pptx_data_path = _write_json(pptx_result, os.path.join(work_dir, "pptx_content.json"))

    print("\n[5/8] Fusing sources into one timeline...")
    combined = fuse_lecture_data(audio_data_path, screen_data_path, pptx_data_path)
    combined_path = _write_json(combined, os.path.join(work_dir, "combined_lecture.json"))
    print(f"  Sources used: {', '.join(combined['sources_used'])}, "
          f"{len(combined['timeline'])} timeline events")

    print("\n[6/8] Chunking timeline...")
    chunks = build_chunks(combined_path, chunk_duration_sec, overlap_sec)
    chunks_path = _write_json(chunks, os.path.join(work_dir, "lecture_chunks.json"))
    print(f"  {len(chunks)} chunk(s)")

    print("\n[7/8] Generating notes...")
    full_notes = generate_full_notes(chunks_path, lecture_title)
    notes_path = os.path.join(work_dir, "lecture_notes.md")
    with open(notes_path, "w", encoding="utf-8") as f:
        f.write(full_notes)

    print("\n[7/8] Polishing notes...")
    # generate_notes.py degrades gracefully per-chunk on API failure (a failed
    # chunk becomes a placeholder string, the run continues); polish_notes.py
    # has no such handling and will raise straight out of a single API call.
    # Since polishing runs after the (often slowest/costliest) transcription
    # and notes-generation stages, a bare crash here would discard all of
    # that work. Fall back to the unpolished notes rather than losing the run.
    polished_path = os.path.join(work_dir, "lecture_notes_polished.md")
    try:
        polished = polish_notes(notes_path)
    except Exception as e:
        print(f"  Polishing failed ({e}) — falling back to unpolished notes.")
        polished = full_notes
    with open(polished_path, "w", encoding="utf-8") as f:
        f.write(polished)

    print("\n[8/8] Chunking notes for search + updating index...")
    passages = chunk_notes_for_search(polished_path)
    passages_path = _write_json(passages, os.path.join(work_dir, "search_passages.json"))
    build_index(passages_path, persist_directory=chroma_persist_dir)

    lecture_id = passages[0]["lecture_id"] if passages else None
    print(f"\n=== Done. lecture_id: {lecture_id} ===")
    print(f"Notes: {polished_path}")
    print(f"Indexed for search/quiz under lecture_id '{lecture_id}' in {chroma_persist_dir}/")

    return {
        "lecture_id": lecture_id,
        "work_dir": work_dir,
        "notes_path": polished_path,
        "passages_path": passages_path,
    }


def build_arg_parser():
    p = argparse.ArgumentParser(description="Run the full lecture-to-notes pipeline end to end.")
    p.add_argument("--title", required=True, help="Lecture title (used for notes heading + fallback lecture_id)")
    p.add_argument("--audio", help="Path to lecture audio file")
    p.add_argument("--video", help="Path to screen recording video file")
    p.add_argument("--pptx", help="Path to supplementary PPTX file")
    p.add_argument("--vocab-hint", default="", help="Whisper initial_prompt vocab hint")
    p.add_argument("--force-language", default=None, help="Force Whisper language code, e.g. 'hi'")
    p.add_argument("--model-size", default="small", help="Whisper model size")
    p.add_argument("--work-dir-root", default="pipeline_runs")
    p.add_argument("--chunk-duration", type=int, default=360)
    p.add_argument("--overlap", type=int, default=45)
    return p


if __name__ == "__main__":
    args = build_arg_parser().parse_args()

    if not args.audio and not args.video:
        print("Error: provide at least --audio or --video", file=sys.stderr)
        sys.exit(1)

    run_pipeline(
        lecture_title=args.title,
        audio_path=args.audio,
        video_path=args.video,
        pptx_path=args.pptx,
        vocab_hint=args.vocab_hint,
        force_language=args.force_language,
        model_size=args.model_size,
        work_dir_root=args.work_dir_root,
        chunk_duration_sec=args.chunk_duration,
        overlap_sec=args.overlap,
    )