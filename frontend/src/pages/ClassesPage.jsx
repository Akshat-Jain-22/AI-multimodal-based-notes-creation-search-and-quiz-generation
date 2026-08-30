import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { listMyClasses, createClass, joinClass } from "../api.js";
import { useAuth } from "../context/AuthContext.jsx";
import TraceDivider from "../components/TraceDivider.jsx";

export default function ClassesPage() {
  const { user } = useAuth();
  const [classes, setClasses] = useState(null);
  const [error, setError] = useState(null);

  const [showForm, setShowForm] = useState(false);
  const [name, setName] = useState("");
  const [subject, setSubject] = useState("");
  const [joinCode, setJoinCode] = useState("");
  const [formError, setFormError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  function refresh() {
    listMyClasses()
      .then(setClasses)
      .catch((e) => setError(e.message));
  }

  useEffect(refresh, []);

  async function handleCreate(e) {
    e.preventDefault();
    setFormError(null);
    if (!name.trim()) {
      setFormError("Class name is required.");
      return;
    }
    setSubmitting(true);
    try {
      await createClass({ name: name.trim(), subject: subject.trim() });
      setName("");
      setSubject("");
      setShowForm(false);
      refresh();
    } catch (e) {
      setFormError(e.message);
    } finally {
      setSubmitting(false);
    }
  }

  async function handleJoin(e) {
    e.preventDefault();
    setFormError(null);
    if (!joinCode.trim()) {
      setFormError("Join code is required.");
      return;
    }
    setSubmitting(true);
    try {
      await joinClass({ joinCode: joinCode.trim() });
      setJoinCode("");
      setShowForm(false);
      refresh();
    } catch (e) {
      setFormError(e.message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div>
      <span className="eyebrow">{user.role === "teacher" ? "Teaching" : "Enrolled"}</span>
      <h1>Your classes</h1>
      <p className="muted">
        {user.role === "teacher"
          ? "Each class here is one section you teach lectures, search, and quizzes stay scoped to it independently."
          : "Each class is independent notes, search, and quizzes never cross between them."}
      </p>

      <TraceDivider />

      {error && <div className="error-box">{error}</div>}

      {!showForm && (
        <button
          className="btn"
          onClick={() => {
            setShowForm(true);
            setFormError(null);
          }}
        >
          {user.role === "teacher" ? "Create a class" : "Join a class"}
        </button>
      )}

      {showForm && (
        <div className="card" style={{ marginBottom: 20 }}>
          {formError && <div className="error-box">{formError}</div>}

          {user.role === "teacher" ? (
            <form onSubmit={handleCreate}>
              <div className="field">
                <label htmlFor="className">Class name</label>
                <input
                  id="className"
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g. Basic Electronics — Section A"
                />
              </div>
              <div className="field">
                <label htmlFor="classSubject">Subject (optional)</label>
                <input
                  id="classSubject"
                  type="text"
                  value={subject}
                  onChange={(e) => setSubject(e.target.value)}
                  placeholder="e.g. Electronics"
                />
              </div>
              <div style={{ display: "flex", gap: 8 }}>
                <button className="btn" type="submit" disabled={submitting}>
                  {submitting ? "Creating…" : "Create"}
                </button>
                <button className="btn btn-secondary" type="button" onClick={() => setShowForm(false)}>
                  Cancel
                </button>
              </div>
            </form>
          ) : (
            <form onSubmit={handleJoin}>
              <div className="field">
                <label htmlFor="joinCode">Join code</label>
                <input
                  id="joinCode"
                  type="text"
                  value={joinCode}
                  onChange={(e) => setJoinCode(e.target.value.toUpperCase())}
                  placeholder="e.g. L9P2MA"
                />
              </div>
              <div style={{ display: "flex", gap: 8 }}>
                <button className="btn" type="submit" disabled={submitting}>
                  {submitting ? "Joining…" : "Join"}
                </button>
                <button className="btn btn-secondary" type="button" onClick={() => setShowForm(false)}>
                  Cancel
                </button>
              </div>
            </form>
          )}
        </div>
      )}

      {classes && classes.length === 0 && (
        <div className="empty-state">
          {user.role === "teacher"
            ? "You haven't created any classes yet."
            : "You haven't joined any classes yet — ask your teacher for a join code."}
        </div>
      )}

      {classes &&
        classes.map((c) => (
          <Link
            key={c.id}
            to={`/classes/${c.id}/lectures`}
            style={{ textDecoration: "none", color: "inherit" }}
          >
            <div className="card card-clickable">
              <span className="eyebrow">{c.subject || "Class"}</span>
              <h3 style={{ margin: 0 }}>{c.name}</h3>
              {user.role === "teacher" && (
                <p className="muted" style={{ margin: "4px 0 0" }}>
                  Join code: <code>{c.join_code}</code>
                </p>
              )}
            </div>
          </Link>
        ))}
    </div>
  );
}
