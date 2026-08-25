import json
import sys


def chunk_timeline(combined_data, chunk_duration_sec=360):
    """Split the combined timeline into chunks of roughly chunk_duration_sec each."""
    timeline = combined_data["timeline"]

    if not timeline:
        return []

    chunks = []
    current_chunk = []
    chunk_start_time = timeline[0]["timestamp"]

    for event in timeline:
        if event["timestamp"] - chunk_start_time >= chunk_duration_sec and current_chunk:
            chunks.append(current_chunk)
            current_chunk = []
            chunk_start_time = event["timestamp"]

        current_chunk.append(event)

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def format_chunk_as_text(chunk_events):
    """Convert a chunk's events into a single readable text block, interleaving
    audio narration and screen content in chronological order."""
    lines = []
    for event in chunk_events:
        ts = event["timestamp"]
        source = event["source"]
        content = event.get("content", "").strip()

        if not content:
            continue

        if source == "audio":
            lines.append(f"[{ts:.1f}s] SPOKEN: {content}")
        elif source == "screen":
            image_note = f" (image saved: {event['image_file']})" if event.get("image_file") else ""
            lines.append(f"[{ts:.1f}s] ON SCREEN: {content}{image_note}")

    return "\n".join(lines)


def collect_diagram_images(chunk_events, min_ocr_length=5, max_ocr_length=100):
    """Identify screen events likely to be genuine diagrams — these have SOME
    OCR text (component labels, small annotations) but not enough to be a
    fully readable paragraph, distinguishing them from both:
      - blank/near-blank frames (near-zero OCR text) — not worth embedding
      - text-heavy slides (long OCR text) — already well covered by OCR text
    """
    diagram_images = []
    seen_files = set()

    for event in chunk_events:
        if event["source"] != "screen":
            continue
        image_file = event.get("image_file")
        if not image_file or image_file in seen_files:
            continue

        ocr_text = (event.get("content", "") or "").strip()
        if min_ocr_length <= len(ocr_text) < max_ocr_length:
            diagram_images.append({
                "timestamp": event["timestamp"],
                "image_file": image_file,
                "ocr_text": ocr_text
            })
            seen_files.add(image_file)

    return diagram_images


def build_chunks(combined_lecture_path, chunk_duration_sec=360, overlap_sec=45):
    """Split lecture into chunks, with each chunk carrying a short lead-in
    context (the last `overlap_sec` seconds of the previous chunk) so the LLM
    can resolve things that started before the chunk boundary but conclude
    just after it (e.g. a calculation split across two chunks)."""
    with open(combined_lecture_path, "r", encoding="utf-8") as f:
        combined_data = json.load(f)

    raw_chunks = chunk_timeline(combined_data, chunk_duration_sec)
    timeline = combined_data["timeline"]

    formatted_chunks = []
    for i, chunk_events in enumerate(raw_chunks, start=1):
        start_time = chunk_events[0]["timestamp"]
        end_time = chunk_events[-1]["timestamp"]

        context_events = [
            e for e in timeline
            if start_time - overlap_sec <= e["timestamp"] < start_time
        ]

        context_text = format_chunk_as_text(context_events) if context_events else ""
        main_text = format_chunk_as_text(chunk_events)
        diagram_images = collect_diagram_images(chunk_events)

        formatted_chunks.append({
            "chunk_number": i,
            "start_time": round(start_time, 1),
            "end_time": round(end_time, 1),
            "context_text": context_text,
            "text": main_text,
            "event_count": len(chunk_events),
            "diagram_images": diagram_images
        })

    return formatted_chunks


if __name__ == "__main__":
    combined_path = sys.argv[1] if len(sys.argv) > 1 else "combined_lecture.json"
    chunk_duration = int(sys.argv[2]) if len(sys.argv) > 2 else 360
    overlap = int(sys.argv[3]) if len(sys.argv) > 3 else 45

    chunks = build_chunks(combined_path, chunk_duration, overlap)

    with open("lecture_chunks.json", "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)

    print(f"Split lecture into {len(chunks)} chunks (~{chunk_duration}s each, {overlap}s overlap)")
    for c in chunks:
        print(f"  Chunk {c['chunk_number']}: {c['start_time']}s - {c['end_time']}s "
              f"({c['event_count']} events, {len(c['text'])} chars, "
              f"{len(c['context_text'])} chars context)")
    print("Saved to lecture_chunks.json")