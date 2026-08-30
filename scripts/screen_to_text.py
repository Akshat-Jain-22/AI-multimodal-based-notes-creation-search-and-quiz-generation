import cv2
import pytesseract
import json
import sys
import os
from PIL import Image
import numpy as np


def frame_difference(frame1, frame2, threshold=30, percent_trigger=1.0):
    """Returns True if frames differ significantly (content changed)."""
    gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
    diff = cv2.absdiff(gray1, gray2)
    non_zero_count = np.count_nonzero(diff > threshold)
    percent_changed = (non_zero_count / diff.size) * 100
    return percent_changed > percent_trigger


def extract_screen_content(video_path, sample_interval_sec=5, percent_trigger=1.0):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    if not fps or fps <= 0:
        fps = 30  # sane fallback if metadata is missing
    frame_interval = int(fps * sample_interval_sec)

    video_basename = os.path.splitext(os.path.basename(video_path))[0]
    images_dir = os.path.join("extracted_images", video_basename)
    os.makedirs(images_dir, exist_ok=True)

    events = []
    prev_frame = None
    frame_idx = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_idx % frame_interval == 0:
            timestamp = frame_idx / fps

            if prev_frame is None or frame_difference(prev_frame, frame, percent_trigger=percent_trigger):
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_img = Image.fromarray(rgb_frame)

                ocr_text = pytesseract.image_to_string(pil_img).strip()

                img_filename = f"frame_{round(timestamp,1)}s.png"
                img_path = os.path.join(images_dir, img_filename)
                pil_img.save(img_path)

                events.append({
                    "timestamp": round(timestamp, 2),
                    "ocr_text": ocr_text,
                    "image_file": img_path
                })
                print(f"[{timestamp:.2f}s] Captured — OCR: {len(ocr_text)} chars, saved: {img_filename}")

                prev_frame = frame

        frame_idx += 1

    cap.release()
    return {"video_source": video_path, "images_directory": images_dir, "events": events}


if __name__ == "__main__":
    video_file = sys.argv[1] if len(sys.argv) > 1 else "screen_recording.mp4"
    result = extract_screen_content(video_file)

    with open("screen_content.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\nExtracted {len(result['events'])} content-change events to screen_content.json")
    print(f"Images saved to: {result['images_directory']}/")