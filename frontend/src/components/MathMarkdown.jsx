import ReactMarkdown from "react-markdown";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";


function normalizeMathDelimiters(text) {
  if (!text) return text;

  let out = text
    .replace(/(?<!\\)\\\[/g, "$$$$")
    .replace(/(?<!\\)\\\]/g, "$$$$")
    .replace(/(?<!\\)\\\(/g, "$")
    .replace(/(?<!\\)\\\)/g, "$");

  const dollarCount = (out.match(/\$/g) || []).length;
  if (dollarCount % 2 !== 0) {
    out += "$";
  }

  return out;
}

export default function MathMarkdown({ children }) {
  return (
    <ReactMarkdown remarkPlugins={[remarkMath]} rehypePlugins={[rehypeKatex]}>
      {normalizeMathDelimiters(children)}
    </ReactMarkdown>
  );
}
