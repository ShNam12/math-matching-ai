import katex from "katex";
import "katex/dist/katex.min.css";

export default function LatexInline({ value, className = "" }) {
  let html;

  try {
    html = katex.renderToString(value || "", {
      throwOnError: false,
      displayMode: false,
    });
  } catch {
    html = value || "";
  }

  return (
    <span
      className={className}
      dangerouslySetInnerHTML={{ __html: html }}
    />
  );
}