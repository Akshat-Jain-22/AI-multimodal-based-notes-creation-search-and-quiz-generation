import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { getClassRoster, removeStudentFromClass } from "../api.js";
import TraceDivider from "../components/TraceDivider.jsx";

export default function RosterPage() {
  const { classId } = useParams();
  const [roster, setRoster] = useState(null);
  const [error, setError] = useState(null);
  const [removingId, setRemovingId] = useState(null);
  const [confirmingId, setConfirmingId] = useState(null);

  function refresh() {
    getClassRoster(classId)
      .then(setRoster)
      .catch((e) => setError(e.message));
  }

  useEffect(() => {
    setRoster(null);
    setError(null);
    refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [classId]);

  async function handleRemove(studentId) {
    setRemovingId(studentId);
    setError(null);
    try {
      await removeStudentFromClass(classId, studentId);
      setConfirmingId(null);
      refresh();
    } catch (e) {
      setError(e.message);
    } finally {
      setRemovingId(null);
    }
  }

  return (
    <div>
      <span className="eyebrow">Roster</span>
      <h1>Enrolled students</h1>
      <p className="muted">
        Removing a student revokes their access to this class's lectures, search, and quizzes
        immediately — they'd need a fresh join code to get back in.
      </p>

      <TraceDivider />

      {error && <div className="error-box">{error}</div>}

      {roster && roster.length === 0 && (
        <div className="empty-state">No students have joined this class yet.</div>
      )}

      {roster &&
        roster.map((s) => (
          <div className="card" key={s.id}>
            <div className="row-between">
              <div>
                <span className="eyebrow">{s.username}</span>
                <h3 style={{ margin: 0 }}>{s.display_name}</h3>
                {s.joined_at && (
                  <p className="muted" style={{ margin: "4px 0 0" }}>
                    Joined {new Date(s.joined_at).toLocaleDateString()}
                  </p>
                )}
              </div>

              {confirmingId === s.id ? (
                <div style={{ display: "flex", gap: 8 }}>
                  <button
                    className="btn btn-danger"
                    onClick={() => handleRemove(s.id)}
                    disabled={removingId === s.id}
                  >
                    {removingId === s.id ? "Removing…" : "Confirm remove"}
                  </button>
                  <button
                    className="btn btn-secondary"
                    onClick={() => setConfirmingId(null)}
                    disabled={removingId === s.id}
                  >
                    Cancel
                  </button>
                </div>
              ) : (
                <button className="btn btn-danger" onClick={() => setConfirmingId(s.id)}>
                  Remove
                </button>
              )}
            </div>
          </div>
        ))}
    </div>
  );
}
