import { Routes, Route, NavLink, useParams, useLocation, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext.jsx";
import ProtectedRoute from "./components/ProtectedRoute.jsx";
import AuthPage from "./pages/AuthPage.jsx";
import ClassesPage from "./pages/ClassesPage.jsx";
import UploadPage from "./pages/UploadPage.jsx";
import LecturesPage from "./pages/LecturesPage.jsx";
import RosterPage from "./pages/RosterPage.jsx";
import NotesPage from "./pages/NotesPage.jsx";
import SearchPage from "./pages/SearchPage.jsx";
import QuizPage from "./pages/QuizPage.jsx";

function NavItem({ to, children, end }) {
  return (
    <NavLink
      to={to}
      end={end}
      className={({ isActive }) => "nav-link" + (isActive ? " active" : "")}
    >
      {children}
    </NavLink>
  );
}

function ClassNav() {
  const { classId } = useParams();
  const { user } = useAuth();

  return (
    <>
      <span className="nav-sep" aria-hidden="true">
        /
      </span>
      {user.role === "teacher" && <NavItem to={`/classes/${classId}/upload`}>Upload</NavItem>}
      {user.role === "teacher" && <NavItem to={`/classes/${classId}/roster`}>Roster</NavItem>}
      <NavItem to={`/classes/${classId}/lectures`}>Lectures</NavItem>
      <NavItem to={`/classes/${classId}/search`}>Search</NavItem>
      <NavItem to={`/classes/${classId}/quiz`}>Quiz</NavItem>
    </>
  );
}

function TopNav() {
  const { user, logout } = useAuth();
  const location = useLocation();
  const inClassRoute = /^\/classes\/[^/]+/.test(location.pathname);

  return (
    <nav className="nav no-print">
      <NavLink to="/" className="nav-brand" end>
        Classroom Notes<span className="dot">.</span>
      </NavLink>

      {user && (
        <Routes>
          <Route path="/classes/:classId/*" element={<ClassNav />} />
        </Routes>
      )}

      {user && (
        <div className="nav-user">
          <span className="muted">
            {user.display_name} · {user.role}
          </span>
          <button className="btn btn-secondary" onClick={logout}>
            Log out
          </button>
        </div>
      )}
    </nav>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <div className="app-shell">
        <TopNav />

        <Routes>
          <Route path="/login" element={<AuthPage />} />

          <Route element={<ProtectedRoute />}>
            <Route path="/" element={<ClassesPage />} />
            <Route path="/classes/:classId/lectures" element={<LecturesPage />} />
            <Route path="/classes/:classId/lectures/:lectureId" element={<NotesPage />} />
            <Route path="/classes/:classId/search" element={<SearchPage />} />
            <Route path="/classes/:classId/quiz" element={<QuizPage />} />
          </Route>

          <Route element={<ProtectedRoute role="teacher" />}>
            <Route path="/classes/:classId/upload" element={<UploadPage />} />
            <Route path="/classes/:classId/roster" element={<RosterPage />} />
          </Route>

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </AuthProvider>
  );
}
