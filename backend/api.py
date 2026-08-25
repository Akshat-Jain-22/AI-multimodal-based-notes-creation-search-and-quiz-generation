"""
api.py — FastAPI backend for local deployment. Multi-tenant version.

Every lecture now belongs to exactly one class (a teacher's one subject-
section). A teacher only manages classes they created; a student only sees
classes they've joined via a join code. Search and quiz are scoped to a
single class at a time — a student with 5 classes gets 5 independent
notebooks, not one merged pool (same as Teams: you're inside one Team's
channel when you search it).

Run locally (unchanged):
    pip install fastapi uvicorn python-multipart
    uvicorn api:app --reload --port 8000

--- What changed from the pre-auth version ---
- jobs.json stays as flat-file job status (unchanged — it's not tenant data).
- lecture_registry.json is GONE. Lecture metadata now lives in db.py's
  SQLite `lectures` table, tied to a class_id.
- Every endpoint except health/auth is behind a login (Depends(get_current_user)),
  and class-mutating endpoints are behind a role check
  (Depends(require_role("teacher"))).
- /search and /quiz now take a class_id and are scoped to that class's
  lectures only, via search_notes.py's new list-aware lecture_id_filter.

--- Scope notes, still true ---
- BackgroundTasks + in-memory-ish jobs.json doesn't survive a server
  restart mid-job — fine for local/small deployment, would need a real task
  queue (Celery/RQ) for production.
"""

import json
import os
import shutil
import subprocess
import sys
import threading
import uuid
from datetime import datetime, timezone
from typing import Optional, Union

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.abspath(os.path.join(THIS_DIR, "..", "scripts"))
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

from dotenv import load_dotenv
load_dotenv(os.path.join(SCRIPTS_DIR, ".env"))

import search_notes
from search_notes import answer_query
from generate_quiz import generate_question_set, format_questions_as_markdown
from build_search_index import get_vectorstore

search_notes.get_vectorstore(os.path.join(SCRIPTS_DIR, "chroma_db"))

CHROMA_PERSIST_DIR = os.path.join(SCRIPTS_DIR, "chroma_db")
PIPELINE_WORK_DIR_ROOT = os.path.join(SCRIPTS_DIR, "pipeline_runs")

UPLOAD_DIR = os.path.join(THIS_DIR, "api_uploads")
JOBS_FILE = os.path.join(THIS_DIR, "jobs.json")

os.makedirs(UPLOAD_DIR, exist_ok=True)
_registry_lock = threading.Lock()

# db.py + auth.py live next to this file in backend/
import db
from auth import router as auth_router, get_current_user, require_role

db.init_db()

app = FastAPI(title="Classroom Notes API", version="0.2.0")
app.include_router(auth_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,  # required for the session cookie to be sent cross-origin (Vite dev server)
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Tiny flat-file persistence helpers (jobs.json only — lectures/classes/users
# are all in db.py now)
# ---------------------------------------------------------------------------

def _load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _update_job(job_id, **fields):
    with _registry_lock:
        jobs = _load_json(JOBS_FILE, {})
        jobs.setdefault(job_id, {})
        jobs[job_id].update(fields)
        _save_json(JOBS_FILE, jobs)


def _get_job(job_id):
    jobs = _load_json(JOBS_FILE, {})
    return jobs.get(job_id)


# ---------------------------------------------------------------------------
# Request/response models
# ---------------------------------------------------------------------------

class CreateClassRequest(BaseModel):
    name: str
    subject: Optional[str] = None


class JoinClassRequest(BaseModel):
    join_code: str


class SearchRequest(BaseModel):
    query: str
    class_id: int


class QuizAPIRequest(BaseModel):
    class_id: int
    topic: str = ""
    format: str = "mcq"
    content_type: str = "theory"
    difficulty: str = "medium"
    count: Union[int, str] = 5
    needs_diagram: bool = False


# ---------------------------------------------------------------------------
# Access-control helper shared by several endpoints below
# ---------------------------------------------------------------------------

def _require_class_access(user, class_id):
    if not db.user_has_access_to_class(user["id"], class_id):
        raise HTTPException(status_code=403, detail="You don't have access to this class.")


def _lecture_ids_for_class(class_id):
    return [l["lecture_id"] for l in db.get_lectures_for_class(class_id)]


# ---------------------------------------------------------------------------
# Background lecture-processing job
# ---------------------------------------------------------------------------

def _run_lecture_job(job_id, title, class_id, requested_by, audio_path, video_path, pptx_path,
                      force_language, model_size="small"):
    """Runs the pipeline in its own subprocess (see pipeline_worker.py's
    docstring for why) rather than calling run_pipeline() directly from this
    background-task thread."""
    _update_job(job_id, status="running")

    job_io_dir = os.path.join(UPLOAD_DIR, job_id)
    os.makedirs(job_io_dir, exist_ok=True)
    input_path = os.path.join(job_io_dir, "pipeline_input.json")
    output_path = os.path.join(job_io_dir, "pipeline_output.json")

    kwargs = {
        "lecture_title": title,
        "audio_path": audio_path,
        "video_path": video_path,
        "pptx_path": pptx_path,
        "force_language": force_language,
        "model_size": model_size,
        "work_dir_root": PIPELINE_WORK_DIR_ROOT,
        "chroma_persist_dir": CHROMA_PERSIST_DIR,
    }
    with open(input_path, "w", encoding="utf-8") as f:
        json.dump(kwargs, f)

    worker_script = os.path.join(THIS_DIR, "pipeline_worker.py")

    try:
        proc = subprocess.run(
            [sys.executable, worker_script, input_path, output_path],
            capture_output=True, text=True,
        )
        if proc.returncode != 0:
            # The worker itself crashed before it could write output_path
            # (e.g. an import error) — surface its stderr, which is far
            # more useful here than a generic "job failed".
            _update_job(job_id, status="error",
                        error=f"Pipeline worker process crashed (exit {proc.returncode}): {proc.stderr[-2000:]}")
            return

        with open(output_path, "r", encoding="utf-8") as f:
            output = json.load(f)

        if output["status"] == "done":
            result = output["result"]
            db.add_lecture(
                lecture_id=result["lecture_id"],
                class_id=class_id,
                title=title,
                notes_path=result["notes_path"],
                work_dir=result["work_dir"],
                uploaded_by=requested_by,
            )
            _update_job(job_id, status="done", result=result)
        else:
            _update_job(job_id, status="error", error=output.get("error", "Unknown pipeline error."))
    except Exception as e:
        _update_job(job_id, status="error", error=str(e))
    finally:
        job_upload_dir = os.path.join(UPLOAD_DIR, job_id)
        shutil.rmtree(job_upload_dir, ignore_errors=True)


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@app.get("/")
def health():
    return {"status": "ok", "docs": "/docs"}


# ---------------------------------------------------------------------------
# Classes
# ---------------------------------------------------------------------------

@app.post("/classes")
def create_class_endpoint(request: CreateClassRequest, user: dict = Depends(require_role("teacher"))):
    cls = db.create_class(request.name, user["id"], subject=request.subject)
    return cls


@app.post("/classes/join")
def join_class_endpoint(request: JoinClassRequest, user: dict = Depends(require_role("student"))):
    try:
        cls = db.join_class(user["id"], request.join_code)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return cls


@app.get("/classes")
def list_my_classes(user: dict = Depends(get_current_user)):
    """Teachers get classes they teach; students get classes they've joined —
    the split students asked for (5 classes, independent of each other)."""
    return db.get_classes_for_user(user)


@app.get("/classes/{class_id}/lectures")
def list_class_lectures(class_id: int, user: dict = Depends(get_current_user)):
    _require_class_access(user, class_id)
    return db.get_lectures_for_class(class_id)


# ---------------------------------------------------------------------------
# Lecture processing
# ---------------------------------------------------------------------------

@app.post("/lectures/process")
async def process_lecture(
    background_tasks: BackgroundTasks,
    title: str = Form(...),
    class_id: int = Form(...),
    force_language: Optional[str] = Form(None),
    model_size: str = Form("small"),
    audio: Union[UploadFile, str, None] = File(None),
    video: Union[UploadFile, str, None] = File(None),
    pptx: Union[UploadFile, str, None] = File(None),
    user: dict = Depends(require_role("teacher")),
):
    # Swagger UI's /docs form sends "" (empty string) for a blank optional
    # file field instead of omitting it, which fails strict UploadFile
    # validation. The only non-UploadFile value that can arrive here is that
    # empty string, so treat any str as "no file" — this also sidesteps
    # isinstance(x, UploadFile) unreliably matching across fastapi's vs
    # starlette's UploadFile classes depending on version.
    if isinstance(audio, str):
        audio = None
    if isinstance(video, str):
        video = None
    if isinstance(pptx, str):
        pptx = None
    if force_language == "":
        force_language = None

    if audio is None and video is None:
        raise HTTPException(
            status_code=400,
            detail="Need at least an audio or video file (same constraint as the pipeline itself).",
        )

    VALID_MODEL_SIZES = {"tiny", "tiny.en", "base", "base.en", "small", "small.en",
                          "medium", "medium.en", "large-v1", "large-v2", "large-v3", "large"}
    if model_size not in VALID_MODEL_SIZES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid model_size '{model_size}'. Choose one of: {', '.join(sorted(VALID_MODEL_SIZES))}. "
                   f"On limited RAM, 'tiny' or 'base' are much faster than 'small' at some accuracy cost.",
        )

    cls = db.get_class(class_id)
    if cls is None:
        raise HTTPException(status_code=404, detail="Unknown class_id.")
    if cls["teacher_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="You can only upload lectures to classes you teach.")

    job_id = uuid.uuid4().hex
    job_upload_dir = os.path.join(UPLOAD_DIR, job_id)
    os.makedirs(job_upload_dir, exist_ok=True)

    async def _save_upload(upload, label):
        if upload is None:
            return None
        dest = os.path.join(job_upload_dir, f"{label}_{upload.filename}")
        with open(dest, "wb") as f:
            shutil.copyfileobj(upload.file, f)
        return dest

    audio_path = await _save_upload(audio, "audio")
    video_path = await _save_upload(video, "video")
    pptx_path = await _save_upload(pptx, "pptx")

    _update_job(job_id, status="queued", title=title, class_id=class_id, requested_by=user["id"], model_size=model_size)
    background_tasks.add_task(
        _run_lecture_job, job_id, title, class_id, user["id"], audio_path, video_path, pptx_path,
        force_language, model_size
    )

    return {"job_id": job_id, "status": "queued"}


@app.get("/lectures/jobs/{job_id}")
def get_job_status(job_id: str, user: dict = Depends(get_current_user)):
    job = _get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Unknown job_id.")
    if job.get("requested_by") != user["id"]:
        raise HTTPException(status_code=403, detail="This job belongs to a different user.")
    return job


@app.get("/lectures/{lecture_id}/notes")
def get_lecture_notes(lecture_id: str, user: dict = Depends(get_current_user)):
    if not db.user_has_access_to_lecture(user["id"], lecture_id):
        raise HTTPException(status_code=403, detail="You don't have access to this lecture.")

    entry = db.get_lecture(lecture_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Unknown lecture_id.")
    if not entry["notes_path"] or not os.path.exists(entry["notes_path"]):
        raise HTTPException(status_code=410, detail="Notes file no longer exists on disk.")

    with open(entry["notes_path"], "r", encoding="utf-8") as f:
        notes_markdown = f.read()
    return {**entry, "notes_markdown": notes_markdown}


# ---------------------------------------------------------------------------
# Search / Quiz — both scoped to one class's lectures at a time
# ---------------------------------------------------------------------------

@app.post("/search")
def search(request: SearchRequest, user: dict = Depends(get_current_user)):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="query cannot be empty.")
    _require_class_access(user, request.class_id)

    lecture_ids = _lecture_ids_for_class(request.class_id)
    if not lecture_ids:
        raise HTTPException(status_code=404, detail="No lectures indexed for this class yet.")

    try:
        result = answer_query(request.query, lecture_id_filter=lecture_ids)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {e}")

    return {"query": request.query, "class_id": request.class_id, **result}


@app.post("/quiz")
def quiz(request: QuizAPIRequest, user: dict = Depends(get_current_user)):
    _require_class_access(user, request.class_id)

    lecture_ids = _lecture_ids_for_class(request.class_id)
    if not lecture_ids:
        raise HTTPException(status_code=404, detail="No lectures indexed for this class yet.")

    req_dict = request.model_dump()
    req_dict.pop("class_id")
    req_dict["lecture_id"] = lecture_ids  # scoped to every lecture in this class

    try:
        result = generate_question_set(req_dict, persist_directory=CHROMA_PERSIST_DIR)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quiz generation failed: {e}")

    return {**result, "markdown": format_questions_as_markdown(result)}


# ---------------------------------------------------------------------------
# Index stats — scoped per class rather than global
# ---------------------------------------------------------------------------

@app.get("/classes/{class_id}/index-stats")
def class_index_stats(class_id: int, user: dict = Depends(get_current_user)):
    _require_class_access(user, class_id)
    lecture_ids = set(_lecture_ids_for_class(class_id))

    vs = get_vectorstore(CHROMA_PERSIST_DIR)
    ids = vs.get()["ids"]
    count = sum(1 for i in ids if i.split("::")[0] in lecture_ids)

    return {"class_id": class_id, "total_passages": count, "lecture_ids": sorted(lecture_ids)}