import { Routes, Route, NavLink } from "react-router-dom";
import UploadPage from "./pages/UploadPage.jsx";
import LecturesPage from "./pages/LecturesPage.jsx";
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

export default function App() {
  return (
    <div className="app-shell">
      <nav className="nav no-print">
        <NavLink to="/" className="nav-brand" end>
          Classroom Notes<span className="dot">.</span>
        </NavLink>
        <NavItem to="/" end>
          Upload
        </NavItem>
        <NavItem to="/lectures">Lectures</NavItem>
        <NavItem to="/search">Search</NavItem>
        <NavItem to="/quiz">Quiz</NavItem>
      </nav>

      <Routes>
        <Route path="/" element={<UploadPage />} />
        <Route path="/lectures" element={<LecturesPage />} />
        <Route path="/lectures/:lectureId" element={<NotesPage />} />
        <Route path="/search" element={<SearchPage />} />
        <Route path="/quiz" element={<QuizPage />} />
      </Routes>
    </div>
  );
}
