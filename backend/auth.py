"""
auth.py — registration/login/logout endpoints and the FastAPI dependency
that resolves "who's calling" for every other protected endpoint in api.py.

Thin on purpose: all the actual persistence (password hashing, session
tokens, expiry) already lives in db.py. This file is just the HTTP-shaped
wrapper around it, plus the session-token transport (a cookie).

Session transport: an httpOnly cookie holding the opaque token from
db.create_session(). Not a JWT — the token is meaningless outside the DB
lookup in db.get_user_by_session(), which is what makes instant logout /
revocation possible (delete the row, the token's dead everywhere).

Wire into api.py with:
    from auth import router as auth_router, get_current_user, require_role
    app.include_router(auth_router)

    @app.get("/something")
    def something(user: dict = Depends(get_current_user)):
        ...

    @app.post("/classes")
    def create_class_endpoint(..., user: dict = Depends(require_role("teacher"))):
        ...
"""

from fastapi import APIRouter, Depends, HTTPException, Response, Cookie
from pydantic import BaseModel

import db
from translate_notes import LANGUAGE_NAMES

router = APIRouter(tags=["auth"])

SESSION_COOKIE_NAME = "session_token"
# Keep in sync with db.SESSION_LIFETIME_HOURS
COOKIE_MAX_AGE_SECONDS = db.SESSION_LIFETIME_HOURS * 3600


# ---------------------------------------------------------------------------
# Request/response models
# ---------------------------------------------------------------------------

class RegisterRequest(BaseModel):
    username: str
    password: str
    role: str  # "teacher" | "student"
    display_name: str = None


class LoginRequest(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    display_name: str
    preferred_language: str


class UpdateLanguageRequest(BaseModel):
    language: str


# ---------------------------------------------------------------------------
# Dependencies — use these in api.py to protect endpoints
# ---------------------------------------------------------------------------

def get_current_user(session_token: str = Cookie(default=None, alias=SESSION_COOKIE_NAME)) -> dict:
    """FastAPI dependency: resolves the logged-in user from the session
    cookie, or raises 401. Use as `Depends(get_current_user)`."""
    if not session_token:
        raise HTTPException(status_code=401, detail="Not logged in.")

    user = db.get_user_by_session(session_token)
    if not user:
        raise HTTPException(status_code=401, detail="Session expired or invalid — please log in again.")

    return user


def require_role(role: str):
    """Dependency factory: use `Depends(require_role('teacher'))` on
    endpoints only that role should reach (e.g. creating a class,
    uploading a lecture)."""

    def _check(user: dict = Depends(get_current_user)) -> dict:
        if user["role"] != role:
            raise HTTPException(
                status_code=403,
                detail=f"This action requires a {role} account.",
            )
        return user

    return _check


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/auth/register", response_model=UserResponse)
def register(request: RegisterRequest, response: Response):
    if request.role not in ("teacher", "student"):
        raise HTTPException(status_code=400, detail="role must be 'teacher' or 'student'.")
    if not request.username.strip() or not request.password:
        raise HTTPException(status_code=400, detail="username and password are required.")
    if len(request.password) < 6:
        raise HTTPException(status_code=400, detail="password must be at least 6 characters.")

    try:
        user_id = db.create_user(
            request.username.strip(),
            request.password,
            request.role,
            display_name=request.display_name,
        )
    except Exception as e:
        # sqlite3.IntegrityError on duplicate username surfaces here
        if "UNIQUE" in str(e):
            raise HTTPException(status_code=409, detail="Username already taken.")
        raise HTTPException(status_code=500, detail=f"Registration failed: {e}")

    token = db.create_session(user_id)
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        httponly=True,
        max_age=COOKIE_MAX_AGE_SECONDS,
        samesite="lax",
    )

    user = db.get_user_by_id(user_id)
    return UserResponse(id=user["id"], username=user["username"], role=user["role"],
                         display_name=user["display_name"], preferred_language=user["preferred_language"])


@router.post("/auth/login", response_model=UserResponse)
def login(request: LoginRequest, response: Response):
    user = db.authenticate_user(request.username.strip(), request.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password.")

    token = db.create_session(user["id"])
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        httponly=True,
        max_age=COOKIE_MAX_AGE_SECONDS,
        samesite="lax",
    )

    return UserResponse(id=user["id"], username=user["username"], role=user["role"],
                         display_name=user["display_name"], preferred_language=user["preferred_language"])


@router.post("/auth/logout")
def logout(response: Response, session_token: str = Cookie(default=None, alias=SESSION_COOKIE_NAME)):
    if session_token:
        db.delete_session(session_token)
    response.delete_cookie(SESSION_COOKIE_NAME)
    return {"status": "logged_out"}


@router.get("/auth/me", response_model=UserResponse)
def me(user: dict = Depends(get_current_user)):
    return UserResponse(id=user["id"], username=user["username"], role=user["role"],
                         display_name=user["display_name"], preferred_language=user["preferred_language"])


@router.patch("/auth/language", response_model=UserResponse)
def update_language(request: UpdateLanguageRequest, user: dict = Depends(get_current_user)):
    """Lets a logged-in user (teacher or student) set the language notes,
    search answers, and quizzes should be shown in for them going forward.
    Validated against translate_notes.py's LANGUAGE_NAMES (which includes
    'en') so a typo/garbage code fails fast here with a clear 400, rather
    than silently reaching the LLM translation step later and producing
    something unpredictable."""
    language = request.language.strip().lower()
    if language not in LANGUAGE_NAMES:
        supported = ", ".join(sorted(LANGUAGE_NAMES.keys()))
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported language '{request.language}'. Supported codes: {supported}.",
        )

    db.set_user_language(user["id"], language)

    updated = db.get_user_by_id(user["id"])
    return UserResponse(id=updated["id"], username=updated["username"], role=updated["role"],
                         display_name=updated["display_name"], preferred_language=updated["preferred_language"])