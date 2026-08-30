import { useEffect, useRef, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { processLecture, getJobStatus } from "../api.js";
import TraceDivider from "../components/TraceDivider.jsx";
import StatusBadge from "../components/StatusBadge.jsx";

const POLL_INTERVAL_MS = 4000;
const MODEL_SIZES = ["tiny", "base", "small", "medium", "large-v3"];

export default function UploadPage() {
  const { classId } = useParams();

  const [title, setTitle] = useState("");
  const [forceLanguage, setForceLanguage] = useState("");
  const [modelSize, setModelSize] = useState("small");
  const [audio, setAudio] = useState(null);
  const [video, setVideo] = useState(null);
  const [pptx, setPptx] = useState(null);

  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState(null);
  const [job, setJob] = useState(null); // { job_id, status, result?, error? }

  const pollRef = useRef(null);

  useEffect(() => {
    return () => clearInterval(pollRef.current);
  }, []);

  function startPolling(jobId) {
    clearInterval(pollRef.current);
    pollRef.current = setInterval(async () => {
      try {
        const status = await getJobStatus(jobId);
        setJob({ job_id: jobId, ...status });
        if (status.status === "done" || status.status === "error") {
          clearInterval(pollRef.current);
        }
      } catch (e) {
        setJob((prev) => ({ ...prev, status: "error", error: e.message }));
        clearInterval(pollRef.current);
      }
    }, POLL_INTERVAL_MS);
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setSubmitError(null);

    if (!title.trim()) {
      setSubmitError("Title is required.");
      return;
    }
    if (!audio && !video) {
      setSubmitError("Provide at least an audio or a video file same as the pipeline itself requires.");
      return;
    }

    setSubmitting(true);
    try {
      const { job_id } = await processLecture({
        title: title.trim(),
        classId,
        audio,
        video,
        pptx,
        forceLanguage: forceLanguage.trim() || undefined,
        modelSize,
      });
      setJob({ job_id, status: "queued" });
      startPolling(job_id);
    } catch (e) {
      setSubmitError(e.message);
    } finally {
      setSubmitting(false);
    }
  }

  function resetForNewUpload() {
    clearInterval(pollRef.current);
    setJob(null);
    setSubmitError(null);
    setTitle("");
    setForceLanguage("");
    setModelSize("small");
    setAudio(null);
    setVideo(null);
    setPptx(null);
  }

  return (
    <div>
      <span className="eyebrow">Ingest</span>
      <h1>Process a lecture</h1>
      <p className="muted">
        Upload audio and/or a screen recording for this class. Transcription and note generation
        run in the background this page polls for progress rather than blocking.
      </p>

      <TraceDivider />

      {!job && (
        <form onSubmit={handleSubmit}>
          {submitError && <div className="error-box">{submitError}</div>}

          <div className="field">
            <label htmlFor="title">Lecture title</label>
            <input
              id="title"
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. Thevenin's Theorem"
            />
          </div>

          <div className="field">
            <label htmlFor="audio">Audio file</label>
            <input
              id="audio"
              type="file"
              accept="audio/*"
              onChange={(e) => setAudio(e.target.files?.[0] || null)}
            />
          </div>

          <div className="field">
            <label htmlFor="video">Screen recording (video)</label>
            <input
              id="video"
              type="file"
              accept="video/*"
              onChange={(e) => setVideo(e.target.files?.[0] || null)}
            />
            <div className="field-hint">At least one of audio or video is required.</div>
          </div>

          <div className="field">
            <label htmlFor="pptx">Slides (optional, .pptx)</label>
            <input
              id="pptx"
              type="file"
              accept=".pptx"
              onChange={(e) => setPptx(e.target.files?.[0] || null)}
            />
          </div>

          <div className="field">
            <label htmlFor="modelSize">Whisper model size</label>
            <select id="modelSize" value={modelSize} onChange={(e) => setModelSize(e.target.value)}>
              {MODEL_SIZES.map((m) => (
                <option key={m} value={m}>
                  {m}
                </option>
              ))}
            </select>
            <div className="field-hint">
              Smaller runs much faster with some accuracy cost "tiny" or "base" is worth trying
              first on limited RAM.
            </div>
          </div>

          <div className="field">
            <label htmlFor="lang">Force language (optional)</label>
            <input
              id="lang"
              type="text"
              value={forceLanguage}
              onChange={(e) => setForceLanguage(e.target.value)}
              placeholder="e.g. hi — leave blank to auto-detect"
            />
          </div>

          <button className="btn" type="submit" disabled={submitting}>
            {submitting ? "Submitting…" : "Process lecture"}
          </button>
        </form>
      )}

      {job && (
        <div className="card">
          <div className="row-between">
            <div>
              <span className="eyebrow">Job {job.job_id?.slice(0, 8)}</span>
              <h3 style={{ margin: 0 }}>{job.title || title}</h3>
            </div>
            <StatusBadge status={job.status} />
          </div>

          {job.status === "queued" && <p className="muted">Waiting to start…</p>}
          {job.status === "running" && (
            <p className="muted">
              Transcribing and generating notes a real lecture can take several minutes. This
              page will update automatically.
            </p>
          )}
          {job.status === "error" && <div className="error-box">{job.error}</div>}
          {job.status === "done" && job.result && (
            <div>
              <p className="muted">
                Indexed as <code>{job.result.lecture_id}</code>
              </p>
              <Link className="btn" to={`/classes/${classId}/lectures/${job.result.lecture_id}`}>
                View notes
              </Link>
            </div>
          )}

          {(job.status === "done" || job.status === "error") && (
            <div style={{ marginTop: 14 }}>
              <button className="btn btn-secondary" onClick={resetForNewUpload}>
                Process another lecture
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
