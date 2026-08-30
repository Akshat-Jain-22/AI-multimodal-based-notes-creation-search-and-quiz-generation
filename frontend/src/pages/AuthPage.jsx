import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";
import TraceDivider from "../components/TraceDivider.jsx";

export default function AuthPage() {
  const { user, login, register } = useAuth();
  const navigate = useNavigate();

  const [mode, setMode] = useState("login"); // "login" | "register"
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("student");
  const [displayName, setDisplayName] = useState("");
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  // Already logged in (e.g. navigated here directly) — bounce to the dashboard.
  useEffect(() => {
    if (user) navigate("/", { replace: true });
  }, [user, navigate]);

  function switchMode(next) {
    setMode(next);
    setError(null);
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);

    if (!username.trim() || !password) {
      setError("Username and password are required.");
      return;
    }

    setSubmitting(true);
    try {
      if (mode === "login") {
        await login({ username: username.trim(), password });
      } else {
        await register({ username: username.trim(), password, role, displayName: displayName.trim() });
      }
      navigate("/");
    } catch (e) {
      setError(e.message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div style={{ maxWidth: 420, margin: "60px auto" }}>
      <span className="eyebrow">{mode === "login" ? "Welcome back" : "Create an account"}</span>
      <h1>Classroom Notes</h1>
      <p className="muted">
        {mode === "login"
          ? "Log in to see your classes."
          : "Register as a teacher to create classes, or a student to join them."}
      </p>

      <TraceDivider />

      <form onSubmit={handleSubmit}>
        {error && <div className="error-box">{error}</div>}

        <div className="field">
          <label htmlFor="username">Username</label>
          <input
            id="username"
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            autoComplete="username"
          />
        </div>

        <div className="field">
          <label htmlFor="password">Password</label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete={mode === "login" ? "current-password" : "new-password"}
          />
        </div>

        {mode === "register" && (
          <>
            <div className="field">
              <label htmlFor="displayName">Display name (optional)</label>
              <input
                id="displayName"
                type="text"
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
              />
            </div>

            <div className="field">
              <label htmlFor="role">I am a</label>
              <select id="role" value={role} onChange={(e) => setRole(e.target.value)}>
                <option value="student">Student</option>
                <option value="teacher">Teacher</option>
              </select>
            </div>
          </>
        )}

        <button className="btn" type="submit" disabled={submitting}>
          {submitting ? "Please wait…" : mode === "login" ? "Log in" : "Register"}
        </button>
      </form>

      <p className="muted" style={{ marginTop: 16 }}>
        {mode === "login" ? (
          <>
            Don't have an account?{" "}
            <a href="#" onClick={(e) => { e.preventDefault(); switchMode("register"); }}>
              Register
            </a>
          </>
        ) : (
          <>
            Already have an account?{" "}
            <a href="#" onClick={(e) => { e.preventDefault(); switchMode("login"); }}>
              Log in
            </a>
          </>
        )}
      </p>
    </div>
  );
}
