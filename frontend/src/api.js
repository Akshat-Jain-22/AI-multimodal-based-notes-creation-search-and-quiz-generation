// All calls to the FastAPI backend go through here. Base URL is
// configurable via .env (VITE_API_BASE_URL) so this doesn't need editing
// if the backend ever runs on a different port/host.
const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function handleResponse(res) {
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail || JSON.stringify(body);
    } catch {
      // response wasn't JSON — fall back to statusText
    }
    throw new Error(detail);
  }
  return res.json();
}

export async function processLecture({ title, audio, video, pptx, forceLanguage }) {
  const form = new FormData();
  form.append("title", title);
  if (forceLanguage) form.append("force_language", forceLanguage);
  if (audio) form.append("audio", audio);
  if (video) form.append("video", video);
  if (pptx) form.append("pptx", pptx);

  const res = await fetch(`${BASE_URL}/lectures/process`, {
    method: "POST",
    body: form,
  });
  return handleResponse(res);
}

export async function getJobStatus(jobId) {
  const res = await fetch(`${BASE_URL}/lectures/jobs/${jobId}`);
  return handleResponse(res);
}

export async function listLectures() {
  const res = await fetch(`${BASE_URL}/lectures`);
  return handleResponse(res);
}

export async function getLectureNotes(lectureId) {
  const res = await fetch(`${BASE_URL}/lectures/${lectureId}/notes`);
  return handleResponse(res);
}

export async function search(query) {
  const res = await fetch(`${BASE_URL}/search`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query }),
  });
  return handleResponse(res);
}

export async function generateQuiz(request) {
  const res = await fetch(`${BASE_URL}/quiz`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });
  return handleResponse(res);
}

export async function getIndexStats() {
  const res = await fetch(`${BASE_URL}/index/stats`);
  return handleResponse(res);
}
