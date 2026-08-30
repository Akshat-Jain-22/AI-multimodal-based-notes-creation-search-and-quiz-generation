"""
db.py — SQLite persistence layer for multi-tenant Classroom Notes.

Replaces the flat jobs.json/lecture_registry.json approach with a real
schema so notes are scoped per class, not global.

Model (Teams-style):
  - A "class" = one teacher's one subject-section (e.g. "Maths - Section A").
    A teacher teaching 3 sections of Maths creates 3 separate classes.
  - Each class has a join_code students use to enroll.
  - Lectures belong to exactly one class. A student only sees lectures for
    classes they're enrolled in; a teacher only sees/manages classes they
    created.
  - Sessions are DB-backed opaque tokens (not JWT) — simplest thing that
    works for a local/small deployment, matches the existing auth.py
    approach (stdlib pbkdf2 + DB session tokens).

Password hashing: stdlib hashlib.pbkdf2_hmac, no external deps.

Usage: call init_db() once at startup (idempotent — CREATE TABLE IF NOT EXISTS).
"""

import sqlite3
import hashlib
import secrets
import string
import os
from datetime import datetime, timezone, timedelta
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "classroom_notes.db")

SESSION_LIFETIME_HOURS = 24 * 7  # 1 week
PBKDF2_ITERATIONS = 260_000


# Connection handling

@contextmanager
def get_connection(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db(db_path=DB_PATH):
    with get_connection(db_path) as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('teacher', 'student')),
            display_name TEXT NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS sessions (
            token TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            created_at TEXT NOT NULL,
            expires_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS classes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            subject TEXT,
            teacher_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            join_code TEXT UNIQUE NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS enrollments (
            student_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            class_id INTEGER NOT NULL REFERENCES classes(id) ON DELETE CASCADE,
            joined_at TEXT NOT NULL,
            PRIMARY KEY (student_id, class_id)
        );

        CREATE TABLE IF NOT EXISTS lectures (
            lecture_id TEXT PRIMARY KEY,
            class_id INTEGER NOT NULL REFERENCES classes(id) ON DELETE CASCADE,
            title TEXT NOT NULL,
            notes_path TEXT,
            work_dir TEXT,
            uploaded_by INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            created_at TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_classes_teacher ON classes(teacher_id);
        CREATE INDEX IF NOT EXISTS idx_enrollments_student ON enrollments(student_id);
        CREATE INDEX IF NOT EXISTS idx_enrollments_class ON enrollments(class_id);
        CREATE INDEX IF NOT EXISTS idx_lectures_class ON lectures(class_id);
        """)


def _now():
    return datetime.now(timezone.utc).isoformat()


# Password hashing

def _hash_password(password, salt=None):
    if salt is None:
        salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), PBKDF2_ITERATIONS
    )
    return digest.hex(), salt


def _verify_password(password, password_hash, salt):
    check, _ = _hash_password(password, salt)
    return secrets.compare_digest(check, password_hash)


# Users

def create_user(username, password, role, display_name=None, db_path=DB_PATH):
    """role: 'teacher' | 'student'. Returns the new user's id.
    Raises sqlite3.IntegrityError if username is taken."""
    password_hash, salt = _hash_password(password)
    with get_connection(db_path) as conn:
        cur = conn.execute(
            "INSERT INTO users (username, password_hash, salt, role, display_name, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (username, password_hash, salt, role, display_name or username, _now()),
        )
        return cur.lastrowid


def get_user_by_id(user_id, db_path=DB_PATH):
    with get_connection(db_path) as conn:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return dict(row) if row else None


def get_user_by_username(username, db_path=DB_PATH):
    with get_connection(db_path) as conn:
        row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        return dict(row) if row else None


def authenticate_user(username, password, db_path=DB_PATH):
    """Returns the user dict (password fields stripped) on success, else None."""
    user = get_user_by_username(username, db_path)
    if not user:
        return None
    if not _verify_password(password, user["password_hash"], user["salt"]):
        return None
    user.pop("password_hash", None)
    user.pop("salt", None)
    return user


# Sessions

def create_session(user_id, db_path=DB_PATH):
    token = secrets.token_urlsafe(32)
    expires_at = (datetime.now(timezone.utc) + timedelta(hours=SESSION_LIFETIME_HOURS)).isoformat()
    with get_connection(db_path) as conn:
        conn.execute(
            "INSERT INTO sessions (token, user_id, created_at, expires_at) VALUES (?, ?, ?, ?)",
            (token, user_id, _now(), expires_at),
        )
    return token


def get_user_by_session(token, db_path=DB_PATH):
    """Returns the user dict if the session is valid and unexpired, else None.
    Lazily deletes the session row if it's found but expired."""
    with get_connection(db_path) as conn:
        row = conn.execute(
            "SELECT s.token, s.expires_at, u.* FROM sessions s "
            "JOIN users u ON u.id = s.user_id WHERE s.token = ?",
            (token,),
        ).fetchone()

        if not row:
            return None

        if datetime.fromisoformat(row["expires_at"]) < datetime.now(timezone.utc):
            conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
            return None

        user = dict(row)
        user.pop("password_hash", None)
        user.pop("salt", None)
        user.pop("token", None)
        user.pop("expires_at", None)
        return user


def delete_session(token, db_path=DB_PATH):
    with get_connection(db_path) as conn:
        conn.execute("DELETE FROM sessions WHERE token = ?", (token,))


# Classes

def _generate_join_code(length=6):
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def create_class(name, teacher_id, subject=None, db_path=DB_PATH):
    """A teacher creates one class (e.g. one section they teach). Returns
    the new class dict including its join_code."""
    with get_connection(db_path) as conn:
        teacher = conn.execute(
            "SELECT role FROM users WHERE id = ?", (teacher_id,)
        ).fetchone()
        if not teacher or teacher["role"] != "teacher":
            raise PermissionError("Only a teacher account can create a class.")

        for _ in range(5):
            join_code = _generate_join_code()
            try:
                cur = conn.execute(
                    "INSERT INTO classes (name, subject, teacher_id, join_code, created_at) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (name, subject, teacher_id, join_code, _now()),
                )
                class_id = cur.lastrowid
                break
            except sqlite3.IntegrityError:
                continue
        else:
            raise RuntimeError("Could not generate a unique join code — try again.")

        row = conn.execute("SELECT * FROM classes WHERE id = ?", (class_id,)).fetchone()
        return dict(row)


def get_class(class_id, db_path=DB_PATH):
    with get_connection(db_path) as conn:
        row = conn.execute("SELECT * FROM classes WHERE id = ?", (class_id,)).fetchone()
        return dict(row) if row else None


def get_class_by_join_code(join_code, db_path=DB_PATH):
    with get_connection(db_path) as conn:
        row = conn.execute(
            "SELECT * FROM classes WHERE join_code = ?", (join_code.strip().upper(),)
        ).fetchone()
        return dict(row) if row else None


def join_class(student_id, join_code, db_path=DB_PATH):
    """Student enrolls in a class via its join code. Idempotent — joining
    twice is a no-op, not an error. Returns the class dict."""
    with get_connection(db_path) as conn:
        student = conn.execute("SELECT role FROM users WHERE id = ?", (student_id,)).fetchone()
        if not student or student["role"] != "student":
            raise PermissionError("Only a student account can join a class.")

        class_row = conn.execute(
            "SELECT * FROM classes WHERE join_code = ?", (join_code.strip().upper(),)
        ).fetchone()
        if not class_row:
            raise ValueError("Invalid join code.")

        conn.execute(
            "INSERT OR IGNORE INTO enrollments (student_id, class_id, joined_at) VALUES (?, ?, ?)",
            (student_id, class_row["id"], _now()),
        )
        return dict(class_row)


def get_classes_for_teacher(teacher_id, db_path=DB_PATH):
    with get_connection(db_path) as conn:
        rows = conn.execute(
            "SELECT * FROM classes WHERE teacher_id = ? ORDER BY created_at DESC", (teacher_id,)
        ).fetchall()
        return [dict(r) for r in rows]


def get_classes_for_student(student_id, db_path=DB_PATH):
    with get_connection(db_path) as conn:
        rows = conn.execute(
            "SELECT c.* FROM classes c "
            "JOIN enrollments e ON e.class_id = c.id "
            "WHERE e.student_id = ? ORDER BY c.created_at DESC",
            (student_id,),
        ).fetchall()
        return [dict(r) for r in rows]


def get_classes_for_user(user, db_path=DB_PATH):
    """Convenience dispatcher — takes a user dict (as returned by
    authenticate_user/get_user_by_session) and returns whichever list applies."""
    if user["role"] == "teacher":
        return get_classes_for_teacher(user["id"], db_path)
    return get_classes_for_student(user["id"], db_path)


# Access control

def user_has_access_to_class(user_id, class_id, db_path=DB_PATH):
    """True if user_id is the teacher who owns class_id, or a student
    enrolled in it."""
    with get_connection(db_path) as conn:
        owns = conn.execute(
            "SELECT 1 FROM classes WHERE id = ? AND teacher_id = ?", (class_id, user_id)
        ).fetchone()
        if owns:
            return True
        enrolled = conn.execute(
            "SELECT 1 FROM enrollments WHERE class_id = ? AND student_id = ?",
            (class_id, user_id),
        ).fetchone()
        return enrolled is not None


def user_has_access_to_lecture(user_id, lecture_id, db_path=DB_PATH):
    with get_connection(db_path) as conn:
        row = conn.execute(
            "SELECT class_id FROM lectures WHERE lecture_id = ?", (lecture_id,)
        ).fetchone()
        if not row:
            return False
        return user_has_access_to_class(user_id, row["class_id"], db_path)


# Lectures

def add_lecture(lecture_id, class_id, title, notes_path, work_dir, uploaded_by, db_path=DB_PATH):
    """Registers a pipeline run's output against a class. uploaded_by must
    be the teacher who owns class_id (checked by the caller/API layer via
    user_has_access_to_class before invoking the pipeline)."""
    with get_connection(db_path) as conn:
        conn.execute(
            "INSERT INTO lectures (lecture_id, class_id, title, notes_path, work_dir, "
            "uploaded_by, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (lecture_id, class_id, title, notes_path, work_dir, uploaded_by, _now()),
        )


def get_lecture(lecture_id, db_path=DB_PATH):
    with get_connection(db_path) as conn:
        row = conn.execute("SELECT * FROM lectures WHERE lecture_id = ?", (lecture_id,)).fetchone()
        return dict(row) if row else None


def get_lectures_for_class(class_id, db_path=DB_PATH):
    with get_connection(db_path) as conn:
        rows = conn.execute(
            "SELECT * FROM lectures WHERE class_id = ? ORDER BY created_at DESC", (class_id,)
        ).fetchall()
        return [dict(r) for r in rows]


def get_lecture_ids_for_user(user_id, db_path=DB_PATH):
    """All lecture_ids visible to this user — across every class they teach
    or are enrolled in. Used to scope search/quiz retrieval by Chroma
    metadata filter (lecture_id is indexed as passage metadata already)."""
    with get_connection(db_path) as conn:
        rows = conn.execute(
            """
            SELECT DISTINCT l.lecture_id FROM lectures l
            WHERE l.class_id IN (
                SELECT id FROM classes WHERE teacher_id = ?
                UNION
                SELECT class_id FROM enrollments WHERE student_id = ?
            )
            """,
            (user_id, user_id),
        ).fetchall()
        return [r["lecture_id"] for r in rows]


def get_enrolled_students(class_id, db_path=DB_PATH):
    with get_connection(db_path) as conn:
        rows = conn.execute(
            "SELECT u.id, u.username, u.display_name, e.joined_at FROM users u "
            "JOIN enrollments e ON e.student_id = u.id "
            "WHERE e.class_id = ? ORDER BY e.joined_at ASC",
            (class_id,),
        ).fetchall()
        return [dict(r) for r in rows]


def remove_student_from_class(student_id, class_id, db_path=DB_PATH):
    """Returns True if an enrollment was actually removed, False if the
    student wasn't enrolled in the first place."""
    with get_connection(db_path) as conn:
        cur = conn.execute(
            "DELETE FROM enrollments WHERE student_id = ? AND class_id = ?",
            (student_id, class_id),
        )
        return cur.rowcount > 0


def delete_lecture(lecture_id, db_path=DB_PATH):
    with get_connection(db_path) as conn:
        conn.execute("DELETE FROM lectures WHERE lecture_id = ?", (lecture_id,))


if __name__ == "__main__":
    init_db()
    print(f"Initialized DB at {DB_PATH}")