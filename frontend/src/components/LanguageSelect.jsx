import { useState } from "react";
import { useAuth } from "../context/AuthContext.jsx";

const SUPPORTED_LANGUAGES = [
  { code: "as", label: "Assamese" },
  { code: "bn", label: "Bengali" },
  { code: "brx", label: "Bodo" },
  { code: "doi", label: "Dogri" },
  { code: "en", label: "English" },
  { code: "gu", label: "Gujarati" },
  { code: "hi", label: "Hindi" },
  { code: "kn", label: "Kannada" },
  { code: "ks", label: "Kashmiri" },
  { code: "kok", label: "Konkani" },
  { code: "mai", label: "Maithili" },
  { code: "ml", label: "Malayalam" },
  { code: "mni", label: "Manipuri (Meitei)" },
  { code: "mr", label: "Marathi" },
  { code: "ne", label: "Nepali" },
  { code: "or", label: "Odia" },
  { code: "pa", label: "Punjabi" },
  { code: "sa", label: "Sanskrit" },
  { code: "sat", label: "Santali" },
  { code: "sd", label: "Sindhi" },
  { code: "ta", label: "Tamil" },
  { code: "te", label: "Telugu" },
  { code: "ur", label: "Urdu" },
];

export default function LanguageSelect() {
  const { user, setLanguage } = useAuth();
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  if (!user) return null;

  async function handleChange(e) {
    const next = e.target.value;
    setSaving(true);
    setError(null);
    try {
      await setLanguage(next);
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="language-select">
      <select
        className="language-select-input"
        value={user.preferred_language || "en"}
        onChange={handleChange}
        disabled={saving}
        aria-label="Content language"
        title="Language for notes, search answers, and quizzes"
      >
        {SUPPORTED_LANGUAGES.map((l) => (
          <option key={l.code} value={l.code}>
            {l.label}
          </option>
        ))}
      </select>
      {error && (
        <span className="language-select-error" role="alert">
          {error}
        </span>
      )}
    </div>
  );
}