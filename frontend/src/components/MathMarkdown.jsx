import ReactMarkdown from "react-markdown";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import { resolveMediaUrl } from "../api.js";

// Renders markdown that may contain LaTeX: $inline$ and $$block$$ math,
// which is exactly how generate_notes.py / polish_notes.py / search_notes.py
// all write formulas (e.g. "$V_{TH} = \\frac{R_L}{R_L + R_{TH}} V_{OC}$").
// Plain react-markdown alone renders that as literal text with dollar signs
// and backslashes still visible — remark-math parses the $...$ syntax and
// rehype-katex typesets it into real math notation.
// The backend prompts the LLM to write math as $inline$ / $$block$$
// (see polish_notes.py), but in practice models often fall back to LaTeX's
// own \(...\) / \[...\] delimiters instead — that's just how LaTeX and most
// textbooks actually write it, and prompting alone doesn't reliably
// override the habit. remark-math only recognizes $ / $$ delimiters, so
// without this, \(...\) and \[...\] render as literal backslash-bracket
// text instead of typeset math. Normalizing here, at the render layer,
// means this keeps working even if a future generation run drifts back to
// LaTeX-style delimiters again.
function normalizeMathDelimiters(text) {
  if (!text) return text;

  let out = text
    // Only treat \( \) \[ \] as math delimiters when NOT preceded by
    // another backslash. A LaTeX matrix/array row-break like "\\[4pt]"
    // (a newline plus 4pt of extra vertical spacing) starts with two
    // backslashes — without this guard, the second backslash + "[" gets
    // misread as an opening math delimiter, corrupting the pairing for
    // every formula that follows it in the document.
    .replace(/(?<!\\)\\\[/g, "$$$$")
    .replace(/(?<!\\)\\\]/g, "$$$$")
    .replace(/(?<!\\)\\\(/g, "$")
    .replace(/(?<!\\)\\\)/g, "$");

  // Best-effort safety net: if the LLM's output got cut off mid-formula
  // (missing a closing delimiter — an occasional generation-time bug,
  // separate from the delimiter-format issue above), there's now one
  // dangling opening delimiter with no match. Left alone, remark-math
  // would treat everything after it as unterminated math and swallow the
  // rest of the document. Closing it here contains the damage to just
  // that one formula instead of breaking every section after it.
  const dollarCount = (out.match(/\$/g) || []).length;
  if (dollarCount % 2 !== 0) {
    out += "$";
  }

  return out;
}

// react-markdown renders an embedded ![alt](src) straight through to a
// plain <img src={src}>. But every image src coming out of notes markdown
// (generate_notes.py's format_diagram_images_markdown(), rewritten by
// api.py's _rewrite_image_paths_to_media_urls()) is a PATH-ONLY backend URL
// like "/lectures/lec1/media/extracted_images/frame.png" — a bare "/..."
// src resolves against the CURRENT PAGE's origin (the Vite dev server),
// not the backend, so without this the image would just 404. This is the
// one place that conversion needs to happen for every image notes markdown
// ever embeds, regardless of which page renders it (NotesPage, SearchPage
// once source snippets get diagram rendering, etc.) — see api.js's
// resolveMediaUrl() for the actual URL-fixing logic.
function MarkdownImage({ src, alt, ...rest }) {
  return <img src={resolveMediaUrl(src)} alt={alt} {...rest} />;
}

export default function MathMarkdown({ children }) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkMath]}
      rehypePlugins={[rehypeKatex]}
      components={{ img: MarkdownImage }}
    >
      {normalizeMathDelimiters(children)}
    </ReactMarkdown>
  );
}