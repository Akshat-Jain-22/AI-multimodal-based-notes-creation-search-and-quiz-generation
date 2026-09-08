// All calls to the FastAPI backend go through here. Base URL is
// configurable via .env (VITE_API_BASE_URL) so this doesn't need editing
// if the backend ever runs on a different port/host.
const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

// api.py's notes/quiz responses embed PATH-ONLY media URLs (e.g.
// "/lectures/lec1/media/extracted_images/frame.png" or
// "/quiz/media/circuit_abc123.svg") — deliberately so, since the backend
// has no reliable way to know its own externally-reachable host (fragile
// behind any proxy/tunnel setup). A bare "/..." src in an <img> tag
// resolves against the CURRENT PAGE's origin, though — which is the
// frontend dev server (localhost:5173), not the backend (localhost:8000)
// — so every such path needs BASE_URL prepended before it's usable.
// Already-absolute URLs (http/https) are passed through untouched, so
// this is safe to apply unconditionally to any image src.
export function resolveMediaUrl(path) {
  if (!path) return path;
  if (path.startsWith("http://") || path.startsWith("https://")) return path;
  return `${BASE_URL}${path}`;
}

async function handleResponse(res) {
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail || JSON.stringify(body);
    } catch {
      // response wasn't JSON — fall back to statusText
    }
    const err = new Error(detail);
    err.status = res.status;
    throw err;
  }
  // 204 / empty-body responses (none currently, but safe to guard)
  const text = await res.text();
  return text ? JSON.parse(text) : null;
}

// Every request needs `credentials: "include"` so the httpOnly session
// cookie set by /auth/login actually gets sent back on later requests —
// without this, every protected endpoint 401s even right after logging in.
function request(path, options = {}) {
  return fetch(`${BASE_URL}${path}`, {
    credentials: "include",
    ...options,
  }).then(handleResponse);
}

function jsonRequest(path, method, body) {
  return request(path, {
    method,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

// ---------------------------------------------------------------------------
// Auth
// ---------------------------------------------------------------------------

export function register({ username, password, role, displayName }) {
  return jsonRequest("/auth/register", "POST", {
    username,
    password,
    role,
    display_name: displayName || undefined,
  });
}

export function login({ username, password }) {
  return jsonRequest("/auth/login", "POST", { username, password });
}

export function logout() {
  return request("/auth/logout", { method: "POST" });
}

// Sets the logged-in user's language preference (used to localize notes,
// search answers, and quiz questions everywhere the caller doesn't pass an
// explicit override). Backend validates the code and returns the updated
// user object, same shape as /auth/me.
export function updateLanguage({ language }) {
  return request("/auth/language", {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ language }),
  });
}

// Returns the current user, or null if not logged in (rather than throwing —
// this is meant to be called on app load to decide which screen to show).
export async function getCurrentUser() {
  try {
    return await request("/auth/me");
  } catch (e) {
    if (e.status === 401) return null;
    throw e;
  }
}

// ---------------------------------------------------------------------------
// Classes
// ---------------------------------------------------------------------------

export function createClass({ name, subject }) {
  return jsonRequest("/classes", "POST", { name, subject: subject || undefined });
}

export function joinClass({ joinCode }) {
  return jsonRequest("/classes/join", "POST", { join_code: joinCode });
}

export function listMyClasses() {
  return request("/classes");
}

export function listClassLectures(classId) {
  return request(`/classes/${classId}/lectures`);
}

export function getClassIndexStats(classId) {
  return request(`/classes/${classId}/index-stats`);
}

export function getClassRoster(classId) {
  return request(`/classes/${classId}/roster`);
}

export function removeStudentFromClass(classId, studentId) {
  return request(`/classes/${classId}/roster/${studentId}`, { method: "DELETE" });
}

// ---------------------------------------------------------------------------
// Lectures
// ---------------------------------------------------------------------------

export function processLecture({ title, classId, audio, video, pptx, forceLanguage, modelSize }) {
  const form = new FormData();
  form.append("title", title);
  form.append("class_id", classId);
  if (forceLanguage) form.append("force_language", forceLanguage);
  if (modelSize) form.append("model_size", modelSize);
  if (audio) form.append("audio", audio);
  if (video) form.append("video", video);
  if (pptx) form.append("pptx", pptx);

  return request("/lectures/process", { method: "POST", body: form });
}

export function getJobStatus(jobId) {
  return request(`/lectures/jobs/${jobId}`);
}

// language is optional — omit it (or pass undefined/null) to let the
// backend fall back to the user's saved preferred_language.
export function getLectureNotes(lectureId, language) {
  const query = language ? `?language=${encodeURIComponent(language)}` : "";
  return request(`/lectures/${lectureId}/notes${query}`);
}

export function deleteLecture(lectureId) {
  return request(`/lectures/${lectureId}`, { method: "DELETE" });
}

// ---------------------------------------------------------------------------
// Search / Quiz — both scoped to a single class
// ---------------------------------------------------------------------------

// language is optional — omit it to let the backend fall back to the
// user's saved preferred_language. generateQuiz() below needs no equivalent
// change: language just flows through via its existing ...rest spread when
// the caller includes it in the object.
export function search({ query, classId, language }) {
  return jsonRequest("/search", "POST", { query, class_id: classId, language: language || undefined });
}

export function generateQuiz({ classId, ...rest }) {
  return jsonRequest("/quiz", "POST", { class_id: classId, ...rest });
}