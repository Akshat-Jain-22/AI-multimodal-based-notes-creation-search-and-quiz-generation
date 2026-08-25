import { useEffect, useState } from "react";
import { generateQuiz, listLectures } from "../api.js";
import TraceDivider from "../components/TraceDivider.jsx";
import MathMarkdown from "../components/MathMarkdown.jsx";
import { downloadText, slugForFilename } from "../utils/download.js";

export default function QuizPage() {
  const [lectures, setLectures] = useState([]);

  const [topic, setTopic] = useState("");
  const [format, setFormat] = useState("mcq");
  const [contentType, setContentType] = useState("theory");
  const [difficulty, setDifficulty] = useState("medium");
  const [count, setCount] = useState("5");
  const [needsDiagram, setNeedsDiagram] = useState(false);
  const [lectureId, setLectureId] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [quiz, setQuiz] = useState(null);

  // answers: { [questionIndex]: selectedOptionIndex }
  const [answers, setAnswers] = useState({});
  const [checked, setChecked] = useState(false);

  useEffect(() => {
    listLectures()
      .then(setLectures)
      .catch(() => {
        /* non-fatal — the lecture filter is optional */
      });
  }, []);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!topic.trim()) {
      setError("Topic is required.");
      return;
    }
    setLoading(true);
    setError(null);
    setQuiz(null);
    setAnswers({});
    setChecked(false);

    const countValue = count.trim().toLowerCase() === "all" ? "all" : parseInt(count, 10) || 5;

    try {
      const result = await generateQuiz({
        topic: topic.trim(),
        format,
        content_type: contentType,
        difficulty,
        count: countValue,
        needs_diagram: needsDiagram,
        lecture_id: lectureId || null,
      });
      setQuiz(result);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  function selectAnswer(qIndex, optIndex) {
    if (checked) return;
    setAnswers((prev) => ({ ...prev, [qIndex]: optIndex }));
  }

  function checkAnswers() {
    setChecked(true);
  }

  function retakeQuiz() {
    setAnswers({});
    setChecked(false);
  }

  const score =
    quiz && checked
      ? quiz.questions.filter((q, i) => answers[i] === q.correct_answer_index).length
      : null;

  return (
    <div>
      <span className="eyebrow">Self-test</span>
      <h1>Generate a quiz</h1>
      <p className="muted">Questions are generated from and grounded in your indexed lectures.</p>

      <TraceDivider />

      <form onSubmit={handleSubmit}>
        {error && <div className="error-box">{error}</div>}

        <div className="field">
          <label htmlFor="topic">Topic</label>
          <input
            id="topic"
            type="text"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="e.g. Thevenin's theorem"
          />
        </div>

        <div className="field">
          <label htmlFor="format">Format</label>
          <select id="format" value={format} onChange={(e) => setFormat(e.target.value)}>
            <option value="mcq">Multiple choice</option>
            <option value="one_word">One word</option>
            <option value="short_answer">Short answer</option>
            <option value="long_answer">Long answer</option>
          </select>
        </div>

        <div className="field">
          <label htmlFor="content_type">Content type</label>
          <select
            id="content_type"
            value={contentType}
            onChange={(e) => setContentType(e.target.value)}
          >
            <option value="theory">Theory</option>
            <option value="numerical">Numerical</option>
            <option value="derivation">Derivation</option>
            <option value="descriptive">Descriptive</option>
          </select>
        </div>

        <div className="field">
          <label htmlFor="difficulty">Difficulty</label>
          <select id="difficulty" value={difficulty} onChange={(e) => setDifficulty(e.target.value)}>
            <option value="easy">Easy</option>
            <option value="medium">Medium</option>
            <option value="hard">Hard</option>
          </select>
        </div>

        <div className="field">
          <label htmlFor="count">Number of questions (or "all")</label>
          <input id="count" type="text" value={count} onChange={(e) => setCount(e.target.value)} />
        </div>

        {lectures.length > 0 && (
          <div className="field">
            <label htmlFor="lecture">Restrict to lecture (optional)</label>
            <select id="lecture" value={lectureId} onChange={(e) => setLectureId(e.target.value)}>
              <option value="">All indexed lectures</option>
              {lectures.map((l) => (
                <option key={l.lecture_id} value={l.lecture_id}>
                  {l.title}
                </option>
              ))}
            </select>
          </div>
        )}

        <div className="field field-checkbox">
          <input
            id="diagram"
            type="checkbox"
            checked={needsDiagram}
            onChange={(e) => setNeedsDiagram(e.target.checked)}
          />
          <label htmlFor="diagram">Include diagrams where relevant</label>
        </div>

        <button className="btn" type="submit" disabled={loading}>
          {loading ? "Generating…" : "Generate quiz"}
        </button>
      </form>

      {quiz && (
        <div>
          <TraceDivider />
          <div className="row-between no-print">
            <h2 style={{ margin: 0 }}>{quiz.topic}</h2>
            <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
              {checked && (
                <span className="quiz-score">
                  {score} / {quiz.questions.length}
                </span>
              )}
              <button
                className="btn btn-secondary"
                onClick={() =>
                  downloadText(`${slugForFilename(quiz.topic)}-quiz.md`, quiz.markdown)
                }
              >
                Download .md
              </button>
              <button className="btn" onClick={() => window.print()}>
                Download PDF
              </button>
            </div>
          </div>

          <div className="print-area">
            <h1 className="print-only-title">{quiz.topic}</h1>
            {quiz.questions.map((q, qi) => {
              const hasOptions = Array.isArray(q.options) && q.options.length > 0;
              return (
                <div className="quiz-question card" key={qi}>
                  <div className="quiz-question-text">
                    <MathMarkdown>{`**Q${qi + 1}.** ${q.question}`}</MathMarkdown>
                  </div>

                  {hasOptions ? (
                    <div className="quiz-options">
                      {q.options.map((opt, oi) => {
                        let cls = "quiz-option";
                        if (answers[qi] === oi) cls += " selected";
                        if (checked && oi === q.correct_answer_index) cls += " correct";
                        else if (checked && answers[qi] === oi) cls += " incorrect";
                        return (
                          <div key={oi} className={cls} onClick={() => selectAnswer(qi, oi)}>
                            <span>{String.fromCharCode(65 + oi)}.</span>
                            <div className="quiz-option-text">
                              <MathMarkdown>{opt}</MathMarkdown>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  ) : (
                    <p className="muted no-print" style={{ marginTop: 8 }}>
                      Free-response question — click "Check answers" to reveal the explanation.
                    </p>
                  )}

                  {(checked || true) && q.explanation && (
                    <div className={"quiz-explanation" + (checked ? "" : " pending")}>
                      <MathMarkdown>{q.explanation}</MathMarkdown>
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          <div className="stack no-print" style={{ flexDirection: "row", gap: 10 }}>
            {!checked ? (
              <button className="btn" onClick={checkAnswers}>
                Check answers
              </button>
            ) : (
              <button className="btn btn-secondary" onClick={retakeQuiz}>
                Retake
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
