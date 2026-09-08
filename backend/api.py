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
import re
import shutil
import subprocess
import sys
import threading
import uuid
from datetime import datetime, timezone
from typing import Optional, Union

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
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
from translate_notes import translate_notes as run_notes_translation

search_notes.get_vectorstore(os.path.join(SCRIPTS_DIR, "chroma_db"))

CHROMA_PERSIST_DIR = os.path.join(SCRIPTS_DIR, "chroma_db")
PIPELINE_WORK_DIR_ROOT = os.path.join(SCRIPTS_DIR, "pipeline_runs")
# Quiz-generated diagrams (attach_generated_diagrams() in generate_quiz.py)
# aren't tied to any one lecture's work_dir — a quiz can pull from every
# lecture in a class — so they get their own stable, absolute root instead.
# NOTE: nothing currently cleans this up over time (no DB record, no
# lecture-delete-triggered rmtree the way lecture media gets) — these
# accumulate indefinitely as quizzes are generated. Worth a periodic-cleanup
# follow-up if disk usage becomes a real concern; not solved here.
QUIZ_DIAGRAMS_DIR = os.path.join(SCRIPTS_DIR, "generated_diagrams")

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
    language: Optional[str] = None  # None -> falls back to the user's preferred_language


class QuizAPIRequest(BaseModel):
    class_id: int
    topic: str = ""
    format: str = "mcq"
    content_type: str = "theory"
    difficulty: str = "medium"
    count: Union[int, str] = 5
    needs_diagram: bool = False
    language: Optional[str] = None  # None -> falls back to the user's preferred_language


# ---------------------------------------------------------------------------
# Access-control helper shared by several endpoints below
# ---------------------------------------------------------------------------

def _require_class_access(user, class_id):
    if not db.user_has_access_to_class(user["id"], class_id):
        raise HTTPException(status_code=403, detail="You don't have access to this class.")


def _lecture_ids_for_class(class_id):
    return [l["lecture_id"] for l in db.get_lectures_for_class(class_id)]


def _resolve_language(request_language, user):
    """?language= / request body language wins if the caller passed one
    explicitly; otherwise fall back to the logged-in user's saved
    preference; otherwise English. Shared by the notes, search, and quiz
    endpoints so the three surfaces default consistently. Always lower-cased
    to match how db.py stores/compares users.preferred_language."""
    return (request_language or user.get("preferred_language") or "en").strip().lower()


def _rewrite_quiz_diagram_paths(result):
    """Rewrites each question's diagram image_file (an absolute filesystem
    path, set by attach_generated_diagrams() in generate_quiz.py) into a URL
    the frontend can fetch: /quiz/media/<relative path under QUIZ_DIAGRAMS_DIR>.

    Mutates result["questions"] in place. Paths that don't resolve inside
    QUIZ_DIAGRAMS_DIR are left completely unchanged rather than guessed at —
    same reasoning as _rewrite_image_paths_to_media_urls above.
    """
    diagrams_root = os.path.abspath(QUIZ_DIAGRAMS_DIR)
    for q in result.get("questions", []):
        diagram = q.get("diagram")
        if not diagram or not diagram.get("image_file"):
            continue

        abs_path = os.path.abspath(diagram["image_file"])
        try:
            rel_path = os.path.relpath(abs_path, diagrams_root)
        except ValueError:
            continue  # different drive on Windows — leave unchanged
        if rel_path.startswith(".."):
            continue  # outside the known diagrams root — don't guess a URL

        url_path = rel_path.replace(os.sep, "/")
        diagram["image_file"] = f"/quiz/media/{url_path}"


IMAGE_MARKDOWN_RE = re.compile(r'(!\[[^\]]*\]\()([^)]+)(\))')


def _rewrite_image_paths_to_media_urls(markdown_text, lecture_id, work_dir):
    """Rewrites every embedded image's filesystem path into a URL the
    frontend can actually fetch: /lectures/{lecture_id}/media/<relative path>.

    Pipeline files (generate_notes.py, and translate_notes.py's translated
    output) embed real filesystem paths — correct for THEM to write (see
    screen_to_text.py/pptx_to_text.py's work_dir-anchored absolute paths),
    but a raw filesystem path means nothing to a browser, and baking a
    specific backend host into stored notes files would make them
    non-portable across environments/deployments. This conversion happens
    here, once, at serve time — applied uniformly regardless of which
    _get_notes_markdown branch (English / cached translation / fresh
    translation) produced the text, since translate_notes.py's placeholder
    protection already guarantees image lines pass through translation
    completely untouched, so the same rewrite works identically on any of
    them.

    Paths outside work_dir, or already-external (http/https) URLs, are left
    unchanged rather than guessed at — better to leave a stale/broken path
    visibly as-is than silently construct a URL that serves the wrong file,
    or one the media endpoint below would just reject anyway.
    """
    if not work_dir:
        return markdown_text

    work_dir_abs = os.path.abspath(work_dir)

    def _replace(match):
        prefix, raw_path, suffix = match.group(1), match.group(2), match.group(3)

        if raw_path.startswith("http://") or raw_path.startswith("https://"):
            return match.group(0)

        raw_path_native = raw_path.replace("/", os.sep)
        abs_path = (
            raw_path_native if os.path.isabs(raw_path_native)
            else os.path.abspath(os.path.join(work_dir_abs, raw_path_native))
        )

        try:
            rel_path = os.path.relpath(abs_path, work_dir_abs)
        except ValueError:
            # Different drive on Windows (e.g. C: vs D:) — relpath can't
            # express that as a relative path at all.
            return match.group(0)

        if rel_path.startswith(".."):
            # Resolves outside this lecture's own work_dir — the media
            # endpoint's own path-traversal check would 403 this anyway,
            # so don't construct a URL that's guaranteed to fail.
            return match.group(0)

        url_path = rel_path.replace(os.sep, "/")
        return f"{prefix}/lectures/{lecture_id}/media/{url_path}{suffix}"

    return IMAGE_MARKDOWN_RE.sub(_replace, markdown_text)


def _get_notes_markdown(entry, language):
    """Returns notes markdown for a lecture in the requested language.

    'en' (or unset) always serves the original notes_path directly — no
    translation step, no cache lookup, matches pre-existing behavior exactly.

    Any other language is served from db's lecture_translations cache if a
    row exists and its file is still on disk; otherwise this translates on
    demand (see translate_notes.py), writes the result under this lecture's
    own work_dir/translations/ (so it gets cleaned up for free by the
    existing work_dir rmtree in delete_lecture_endpoint below — no separate
    cleanup path needed), and records the cache row so every student after
    the first one for this (lecture, language) pair gets a cache hit instead
    of paying for another LLM call.

    Falls back to the original English notes on a translation failure —
    English notes beat a 500 error for a student who just wants to read.

    Every returned markdown string has its embedded image paths rewritten
    into fetchable /lectures/{lecture_id}/media/... URLs (see
    _rewrite_image_paths_to_media_urls above) before it ever reaches the
    caller — this is the one place that conversion needs to happen,
    regardless of which branch below produced the raw text.
    """
    lecture_id = entry["lecture_id"]
    work_dir = entry.get("work_dir") or os.path.dirname(entry["notes_path"])

    if not language or language == "en":
        with open(entry["notes_path"], "r", encoding="utf-8") as f:
            markdown, served_language = f.read(), "en"
    else:
        cached = db.get_lecture_translation(lecture_id, language)
        if cached and os.path.exists(cached["notes_path"]):
            with open(cached["notes_path"], "r", encoding="utf-8") as f:
                markdown, served_language = f.read(), language
        else:
            try:
                translated_markdown = run_notes_translation(entry["notes_path"], language)

                translations_dir = os.path.join(work_dir, "translations")
                os.makedirs(translations_dir, exist_ok=True)
                translated_path = os.path.join(translations_dir, f"notes_{language}.md")
                with open(translated_path, "w", encoding="utf-8") as f:
                    f.write(translated_markdown)

                db.add_lecture_translation(lecture_id, language, translated_path)
                markdown, served_language = translated_markdown, language
            except Exception as e:
                print(f"Warning: translation to '{language}' failed for lecture {lecture_id}: {e}")
                with open(entry["notes_path"], "r", encoding="utf-8") as f:
                    markdown, served_language = f.read(), "en"

    markdown = _rewrite_image_paths_to_media_urls(markdown, lecture_id, work_dir)
    return markdown, served_language


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

@app.delete("/lectures/{lecture_id}")
def delete_lecture_endpoint(lecture_id: str, user: dict = Depends(require_role("teacher"))):
    entry = db.get_lecture(lecture_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Unknown lecture_id.")

    cls = db.get_class(entry["class_id"])
    if cls is None or cls["teacher_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="You can only delete lectures from classes you teach.")

    # Remove this lecture's passages from the search index so deleted
    # lectures can't still surface in /search or /quiz results. Passage ids
    # are "{lecture_id}::{section_heading}::{i}" (see chunk_notes_for_search.py),
    # so a prefix match reliably scopes to just this lecture.
    try:
        vs = get_vectorstore(CHROMA_PERSIST_DIR)
        all_ids = vs.get()["ids"]
        ids_to_delete = [i for i in all_ids if i.startswith(f"{lecture_id}::")]
        if ids_to_delete:
            vs.delete(ids=ids_to_delete)
    except Exception as e:
        # Don't block the delete on a Chroma hiccup — the DB row is the
        # source of truth for access control, a stray orphaned passage is
        # a much smaller problem than a delete button that silently fails.
        print(f"Warning: failed to remove Chroma passages for {lecture_id}: {e}")

    # Best-effort cleanup of on-disk notes/transcripts for this lecture.
    if entry.get("work_dir") and os.path.isdir(entry["work_dir"]):
        shutil.rmtree(entry["work_dir"], ignore_errors=True)

    db.delete_lecture(lecture_id)

    return {"status": "deleted", "lecture_id": lecture_id}


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


@app.get("/classes/{class_id}/roster")
def get_class_roster(class_id: int, user: dict = Depends(require_role("teacher"))):
    cls = db.get_class(class_id)
    if cls is None:
        raise HTTPException(status_code=404, detail="Unknown class_id.")
    if cls["teacher_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="You can only view the roster for classes you teach.")
    return db.get_enrolled_students(class_id)


@app.delete("/classes/{class_id}/roster/{student_id}")
def remove_student_endpoint(class_id: int, student_id: int, user: dict = Depends(require_role("teacher"))):
    cls = db.get_class(class_id)
    if cls is None:
        raise HTTPException(status_code=404, detail="Unknown class_id.")
    if cls["teacher_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="You can only manage the roster for classes you teach.")

    removed = db.remove_student_from_class(student_id, class_id)
    if not removed:
        raise HTTPException(status_code=404, detail="That student is not enrolled in this class.")

    return {"status": "removed", "student_id": student_id, "class_id": class_id}


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
def get_lecture_notes(lecture_id: str, language: Optional[str] = None,
                       user: dict = Depends(get_current_user)):
    if not db.user_has_access_to_lecture(user["id"], lecture_id):
        raise HTTPException(status_code=403, detail="You don't have access to this lecture.")

    entry = db.get_lecture(lecture_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Unknown lecture_id.")
    if not entry["notes_path"] or not os.path.exists(entry["notes_path"]):
        raise HTTPException(status_code=410, detail="Notes file no longer exists on disk.")

    # ?language= wins if the caller passed one explicitly; otherwise fall
    # back to the logged-in user's saved preference; otherwise English.
    target_language = _resolve_language(language, user)

    notes_markdown, served_language = _get_notes_markdown(entry, target_language)
    return {**entry, "notes_markdown": notes_markdown, "language": served_language}


@app.get("/lectures/{lecture_id}/media/{file_path:path}")
def get_lecture_media(lecture_id: str, file_path: str, user: dict = Depends(get_current_user)):
    """Serves a single captured image (diagram/circuit/graph screenshot)
    for a lecture — the exact URLs _rewrite_image_paths_to_media_urls()
    above rewrites embedded notes-markdown image paths into.

    Access-controlled the same way as /lectures/{lecture_id}/notes
    (user_has_access_to_lecture) — this is tenant-scoped lecture data, not
    a public static-file mount, so a student in one class can't view
    another class's slides just by knowing or guessing a URL.

    file_path is a URL path segment and therefore attacker-controlled, so
    the resolved path is confirmed to stay INSIDE this lecture's own
    work_dir before anything is served — otherwise something like
    "../../../../some/other/file" could read arbitrary files off disk.
    """
    if not db.user_has_access_to_lecture(user["id"], lecture_id):
        raise HTTPException(status_code=403, detail="You don't have access to this lecture.")

    entry = db.get_lecture(lecture_id)
    if entry is None or not entry.get("work_dir"):
        raise HTTPException(status_code=404, detail="Unknown lecture_id.")

    work_dir = os.path.abspath(entry["work_dir"])
    requested_path = os.path.abspath(os.path.join(work_dir, file_path))

    if not (requested_path == work_dir or requested_path.startswith(work_dir + os.sep)):
        raise HTTPException(status_code=403, detail="Invalid file path.")
    if not os.path.isfile(requested_path):
        raise HTTPException(status_code=404, detail="File not found.")

    return FileResponse(requested_path)


@app.get("/quiz/media/{file_path:path}")
def get_quiz_media(file_path: str, user: dict = Depends(get_current_user)):
    """Serves a single quiz-generated diagram/chart image (see
    attach_generated_diagrams() in generate_quiz.py).

    Deliberately DIFFERENT access control than /lectures/{lecture_id}/media
    above: this is login-only, NOT scoped to a specific class/lecture. A
    quiz can pull content from every lecture in a class via
    lecture_id_filter, so there's no single "owner" record to check access
    against without persisting which class a given quiz belonged to —
    which nothing does today (quiz generation is stateless/on-demand,
    nothing about a generated quiz is saved server-side).

    Judged an acceptable trade-off rather than an oversight: filenames are
    UUID-based (unique_diagram_path/unique_chart_path) and therefore
    unguessable, and the content is synthetic — invented numbers for one
    practice question, not real lecture material — so a logged-in user
    from a different class seeing one is low-severity. If this ever needs
    the same tenant guarantee as lecture media, quiz results would need to
    be persisted with a class_id to check against.

    Still gets the same path-traversal protection as the lecture-media
    endpoint, since file_path is equally attacker-controlled here.
    """
    diagrams_root = os.path.abspath(QUIZ_DIAGRAMS_DIR)
    requested_path = os.path.abspath(os.path.join(diagrams_root, file_path))

    if not (requested_path == diagrams_root or requested_path.startswith(diagrams_root + os.sep)):
        raise HTTPException(status_code=403, detail="Invalid file path.")
    if not os.path.isfile(requested_path):
        raise HTTPException(status_code=404, detail="File not found.")

    return FileResponse(requested_path)


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

    target_language = _resolve_language(request.language, user)

    try:
        result = answer_query(request.query, lecture_id_filter=lecture_ids, language=target_language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {e}")

    return {"query": request.query, "class_id": request.class_id, "language": target_language, **result}


@app.post("/quiz")
def quiz(request: QuizAPIRequest, user: dict = Depends(get_current_user)):
    _require_class_access(user, request.class_id)

    lecture_ids = _lecture_ids_for_class(request.class_id)
    if not lecture_ids:
        raise HTTPException(status_code=404, detail="No lectures indexed for this class yet.")

    req_dict = request.model_dump()
    req_dict.pop("class_id")
    req_dict["lecture_id"] = lecture_ids  # scoped to every lecture in this class
    req_dict["language"] = _resolve_language(request.language, user)

    try:
        result = generate_question_set(req_dict, persist_directory=CHROMA_PERSIST_DIR,
                                        diagram_output_dir=QUIZ_DIAGRAMS_DIR)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quiz generation failed: {e}")

    # Mutates result["questions"] in place, BEFORE format_questions_as_markdown()
    # runs below — that function embeds diagram["image_file"] directly into a
    # Markdown image line, so fixing the field here fixes both the live JSON
    # response AND the downloadable .md's embedded image link in one pass.
    _rewrite_quiz_diagram_paths(result)

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