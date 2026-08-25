import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { listLectures } from "../api.js";
import TraceDivider from "../components/TraceDivider.jsx";

export default function LecturesPage() {
  const [lectures, setLectures] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    listLectures()
      .then(setLectures)
      .catch((e) => setError(e.message));
  }, []);

  return (
    <div>
      <span className="eyebrow">Library</span>
      <h1>Lectures</h1>
      <p className="muted">Everything that's been processed and indexed so far.</p>

      <TraceDivider />

      {error && <div className="error-box">{error}</div>}

      {lectures && lectures.length === 0 && (
        <div className="empty-state">
          Nothing processed yet. <Link to="/">Upload a lecture</Link> to get started.
        </div>
      )}

      {lectures &&
        lectures.map((l) => (
          <Link
            key={l.lecture_id}
            to={`/lectures/${l.lecture_id}`}
            style={{ textDecoration: "none", color: "inherit" }}
          >
            <div className="card card-clickable">
              <span className="eyebrow">{l.lecture_id}</span>
              <h3 style={{ margin: 0 }}>{l.title}</h3>
              {l.created_at && (
                <p className="muted" style={{ margin: "4px 0 0" }}>
                  {new Date(l.created_at).toLocaleString()}
                </p>
              )}
            </div>
          </Link>
        ))}
    </div>
  );
}
