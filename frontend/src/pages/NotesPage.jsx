import { useEffect, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { getLectureNotes, deleteLecture } from "../api.js";
import { useAuth } from "../context/AuthContext.jsx";
import TraceDivider from "../components/TraceDivider.jsx";
import MathMarkdown from "../components/MathMarkdown.jsx";
import { downloadText, slugForFilename } from "../utils/download.js";

export default function NotesPage() {
  const { classId, lectureId } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();

  const [notes, setNotes] = useState(null);
  const [error, setError] = useState(null);

  const [confirmingDelete, setConfirmingDelete] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState(null);

  useEffect(() => {
    setNotes(null);
    setError(null);
    setConfirmingDelete(false);
    getLectureNotes(lectureId)
      .then(setNotes)
      .catch((e) => setError(e.message));
  }, [lectureId]);

  async function handleDelete() {
    setDeleting(true);
    setDeleteError(null);
    try {
      await deleteLecture(lectureId);
      navigate(`/classes/${classId}/lectures`);
    } catch (e) {
      setDeleteError(e.message);
      setDeleting(false);
      setConfirmingDelete(false);
    }
  }

  return (
    <div>
      <Link to={`/classes/${classId}/lectures`} className="muted" style={{ textDecoration: "none" }}>
        ← Back to lectures
      </Link>

      {error && <div className="error-box">{error}</div>}
      {deleteError && <div className="error-box">{deleteError}</div>}

      {notes && (
        <>
          <div className="row-between no-print">
            <div>
              <span className="eyebrow">{notes.lecture_id}</span>
              <h1 style={{ margin: 0 }}>{notes.title}</h1>
            </div>
            <div style={{ display: "flex", gap: 8 }}>
              <button
                className="btn btn-secondary"
                onClick={() =>
                  downloadText(`${slugForFilename(notes.title)}-notes.md`, notes.notes_markdown)
                }
              >
                Download .md
              </button>
              <button className="btn" onClick={() => window.print()}>
                Download PDF
              </button>
              {user.role === "teacher" && !confirmingDelete && (
                <button className="btn btn-danger" onClick={() => setConfirmingDelete(true)}>
                  Delete
                </button>
              )}
            </div>
          </div>

          {confirmingDelete && (
            <div className="card card-danger">
              <p style={{ margin: 0 }}>
                Delete <strong>{notes.title}</strong>? This removes the notes, its search index
                entries, and cannot be undone.
              </p>
              <div style={{ display: "flex", gap: 8, marginTop: 12 }}>
                <button className="btn btn-danger" onClick={handleDelete} disabled={deleting}>
                  {deleting ? "Deleting…" : "Yes, delete"}
                </button>
                <button
                  className="btn btn-secondary"
                  onClick={() => setConfirmingDelete(false)}
                  disabled={deleting}
                >
                  Cancel
                </button>
              </div>
            </div>
          )}

          <TraceDivider />
          <div className="notes-content print-area">
            <h1 className="print-only-title">{notes.title}</h1>
            <MathMarkdown>{notes.notes_markdown}</MathMarkdown>
          </div>
        </>
      )}

      {!notes && !error && <p className="muted">Loading…</p>}
    </div>
  );
}
