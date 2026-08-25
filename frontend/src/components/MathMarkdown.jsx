import ReactMarkdown from "react-markdown";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";

// Renders markdown that may contain LaTeX: $inline$ and $$block$$ math,
// which is exactly how generate_notes.py / polish_notes.py / search_notes.py
// all write formulas (e.g. "$V_{TH} = \\frac{R_L}{R_L + R_{TH}} V_{OC}$").
// Plain react-markdown alone renders that as literal text with dollar signs
// and backslashes still visible — remark-math parses the $...$ syntax and
// rehype-katex typesets it into real math notation.
export default function MathMarkdown({ children }) {
  return (
    <ReactMarkdown remarkPlugins={[remarkMath]} rehypePlugins={[rehypeKatex]}>
      {children}
    </ReactMarkdown>
  );
}
