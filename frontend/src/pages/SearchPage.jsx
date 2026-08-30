import { useState } from "react";
import { useParams } from "react-router-dom";
import { search } from "../api.js";
import TraceDivider from "../components/TraceDivider.jsx";
import MathMarkdown from "../components/MathMarkdown.jsx";
import { downloadText, slugForFilename } from "../utils/download.js";

export default function SearchPage() {
  const { classId } = useParams();
  const [query, setQuery] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const res = await search({ query: query.trim(), classId });
      setResult(res);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  function handleDownload() {
    if (!result) return;
    const lines = [
      `# Search: ${result.query}`,
      "",
      "## Answer",
      "",
      result.answer,
      "",
    ];
    if (result.sources.length > 0) {
      lines.push("## Sources", "");
      result.sources.forEach((s) => {
        lines.push(
          `- **${s.lecture_title} — ${s.section_heading}** (score ${s.score.toFixed(3)})`,
          "",
          s.text,
          ""
        );
      });
    }
    downloadText(`${slugForFilename(result.query)}-search.md`, lines.join("\n"));
  }

  return (
    <div>
      <span className="eyebrow">Grounded Q&amp;A</span>
      <h1>Search this class's lectures</h1>
      <p className="muted">
        Answers are grounded only in lectures indexed for this class if nothing relevant is
        indexed here, it says so rather than guessing.
      </p>

      <TraceDivider />

      <form onSubmit={handleSubmit} className="search-bar">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="e.g. How do you find the Thevenin resistance?"
        />
        <button className="btn" type="submit" disabled={loading}>
          {loading ? "Searching…" : "Search"}
        </button>
      </form>

      {error && <div className="error-box">{error}</div>}

      {result && (
        <div>
          <TraceDivider />
          <div className="row-between no-print">
            <h2 style={{ margin: 0 }}>Answer</h2>
            <div style={{ display: "flex", gap: 8 }}>
              <button className="btn btn-secondary" onClick={handleDownload}>
                Download .md
              </button>
              <button className="btn" onClick={() => window.print()}>
                Download PDF
              </button>
            </div>
          </div>
          <div className="print-area">
            <div className="notes-content">
              <h1 className="print-only-title">{result.query}</h1>
              <MathMarkdown>{result.answer}</MathMarkdown>
            </div>

            {result.sources.length > 0 && (
              <>
                <h3 style={{ marginTop: 28 }}>Sources ({result.sources.length})</h3>
                <div className="stack">
                  {result.sources.map((s, i) => (
                    <div className="source-item" key={i}>
                      <div className="score">
                        {s.lecture_title} — {s.section_heading} · score {s.score.toFixed(3)}
                      </div>
                      <p style={{ margin: "4px 0 0" }}>{s.text}</p>
                    </div>
                  ))}
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
