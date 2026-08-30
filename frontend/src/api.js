const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function handleResponse(res) {
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail || JSON.stringify(body);
    } catch {
      
    }
    const err = new Error(detail);
    err.status = res.status;
    throw err;
  }
 
  const text = await res.text();
  return text ? JSON.parse(text) : null;
}

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

// Auth

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

// Classes

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

// Lectures

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

export function getLectureNotes(lectureId) {
  return request(`/lectures/${lectureId}/notes`);
}

export function deleteLecture(lectureId) {
  return request(`/lectures/${lectureId}`, { method: "DELETE" });
}

// Search / Quiz — both scoped to a single class

export function search({ query, classId }) {
  return jsonRequest("/search", "POST", { query, class_id: classId });
}

export function generateQuiz({ classId, ...rest }) {
  return jsonRequest("/quiz", "POST", { class_id: classId, ...rest });
}
