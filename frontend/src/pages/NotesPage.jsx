import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { getLectureNotes } from "../api.js";
import TraceDivider from "../components/TraceDivider.jsx";
import MathMarkdown from "../components/MathMarkdown.jsx";
import { downloadText, slugForFilename } from "../utils/download.js";

export default function NotesPage() {
  const { lectureId } = useParams();
  const [notes, setNotes] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    setNotes(null);
    setError(null);
    getLectureNotes(lectureId)
      .then(setNotes)
      .catch((e) => setError(e.message));
  }, [lectureId]);

  return (
    <div>
      <Link to="/lectures" className="muted" style={{ textDecoration: "none" }}>
        ← Back to lectures
      </Link>

      {error && <div className="error-box">{error}</div>}

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
            </div>
          </div>
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
