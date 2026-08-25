// Triggers a browser download of plain text content — no backend involved,
// since everything being downloaded (notes markdown, quiz markdown, a
// search summary) is already sitting in the page's own state after fetch.
export function downloadText(filename, content) {
  const blob = new Blob([content], { type: "text/markdown;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

// Safe-ish filename from arbitrary text (a title, a query, etc.)
export function slugForFilename(text, maxLength = 60) {
  return (
    text
      .toLowerCase()
      .trim()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-+|-+$/g, "")
      .slice(0, maxLength) || "download"
  );
}
