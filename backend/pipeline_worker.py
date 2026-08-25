"""
pipeline_worker.py — runs run_pipeline() in its own OS process.

Why this exists: faster-whisper/ctranslate2 relies on native OpenMP
threading internally. On Windows, initializing that from a thread that
ISN'T the process's actual main thread (which is exactly what FastAPI's
BackgroundTasks uses — a worker thread from anyio's threadpool) has a
known hang/deadlock failure mode: high CPU, zero progress, no error, no
timeout. The standalone CLI scripts (audio_to_text.py etc.) never hit this
because they always run directly on the process's main thread.

Spawning a genuine subprocess sidesteps this completely — the child
process's main thread is its own main thread regardless of who spawned it,
so ctranslate2 initializes exactly like it does when you run the CLI
scripts by hand.

Usage: python pipeline_worker.py <input_json_path> <output_json_path>
  input_json_path  — JSON dict of run_pipeline() kwargs
  output_json_path — written with either
      {"status": "done", "result": {...}}
    or
      {"status": "error", "error": "..."}
  Always exits 0 on a handled error (the error is IN the output JSON) so
  the caller can distinguish "pipeline failed" from "worker itself crashed"
  by checking the JSON contents vs. the subprocess exit code.
"""

import sys
import os
import json

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.abspath(os.path.join(THIS_DIR, "..", "scripts"))
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

from dotenv import load_dotenv
load_dotenv(os.path.join(SCRIPTS_DIR, ".env"))

from run_pipeline import run_pipeline


def main():
    if len(sys.argv) != 3:
        print("Usage: python pipeline_worker.py <input_json_path> <output_json_path>", file=sys.stderr)
        sys.exit(2)

    input_path, output_path = sys.argv[1], sys.argv[2]

    with open(input_path, "r", encoding="utf-8") as f:
        kwargs = json.load(f)

    try:
        result = run_pipeline(**kwargs)
        output = {"status": "done", "result": result}
    except Exception as e:
        output = {"status": "error", "error": str(e)}

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()