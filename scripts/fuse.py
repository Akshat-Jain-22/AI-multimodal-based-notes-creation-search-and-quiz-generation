import json
import sys
import os


def load_json_if_exists(path):
    """Safely load a JSON file if it exists, else return None."""
    if path and os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def build_audio_events(audio_data):
    """Convert audio transcript data into timeline events.
    Handles both the raw segments format (audio_transcript.json) and the
    whole-document translated format (audio_transcript_translated.json)."""
    events = []

    if not audio_data:
        return events

    # Case 1: segment-level data (has "segments" with start/end + text)
    # Supports both the raw audio_to_text.py output (field "text") and the
    # translate_transcript.py output (field "translated_text").
    if "segments" in audio_data:
        for seg in audio_data["segments"]:
            content = seg.get("translated_text") or seg.get("text", "")
            events.append({
                "timestamp": seg["start"],
                "source": "audio",
                "content": content
            })

    # Case 2: whole-document translated data (single translated_text, no per-segment timestamps)
    elif "translated_text" in audio_data:
        events.append({
            "timestamp": 0.0,
            "source": "audio",
            "content": audio_data["translated_text"],
            "note": "whole-document translation, no per-segment timestamps available"
        })

    return events


def build_screen_events(screen_data):
    """Convert screen_to_text.py output into timeline events."""
    events = []

    if not screen_data:
        return events

    for event in screen_data.get("events", []):
        events.append({
            "timestamp": event["timestamp"],
            "source": "screen",
            "content": event.get("ocr_text", ""),
            "image_file": event.get("image_file")
        })

    return events


def fuse_lecture_data(audio_path=None, screen_path=None, pptx_path=None):
    audio_data = load_json_if_exists(audio_path)
    screen_data = load_json_if_exists(screen_path)
    pptx_data = load_json_if_exists(pptx_path)

    sources_found = []
    if audio_data:
        sources_found.append("audio")
    if screen_data:
        sources_found.append("screen")
    if pptx_data:
        sources_found.append("pptx (supplementary)")

    if not audio_data and not screen_data:
        raise ValueError(
            "No timestamped source available (need at least audio or screen capture) — "
            "cannot build a lecture timeline from PPTX alone."
        )

    timeline = []
    timeline.extend(build_audio_events(audio_data))
    timeline.extend(build_screen_events(screen_data))

    # Sort everything chronologically into one unified timeline
    timeline.sort(key=lambda x: x["timestamp"])

    result = {
        "sources_used": sources_found,
        "timeline": timeline,
        "supplementary_pptx": pptx_data  # not merged into timeline; available as reference
    }

    return result


if __name__ == "__main__":
    # Usage: python fuse_lecture_data.py [audio_json] [screen_json] [pptx_json]
    # Any argument can be omitted/empty if that source isn't available for this lecture
    audio_path = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] != "-" else None
    screen_path = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] != "-" else None
    pptx_path = sys.argv[3] if len(sys.argv) > 3 and sys.argv[3] != "-" else None

    result = fuse_lecture_data(audio_path, screen_path, pptx_path)

    with open("combined_lecture.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"Sources used: {', '.join(result['sources_used'])}")
    print(f"Total timeline events: {len(result['timeline'])}")
    print("Saved to combined_lecture.json")