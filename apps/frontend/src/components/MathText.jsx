import LatexInline from "./LatexInline";

export default function MathText({ value, className = "" }) {
  const text = value || "";
  const parts = text.split(/(\$[^$]+\$)/g);

  return (
    <span className={className}>
      {parts.map((part, index) => {
        if (part.startsWith("$") && part.endsWith("$")) {
          const latex = part.slice(1, -1);

          return (
            <LatexInline
              key={`${part}-${index}`}
              value={latex}
            />
          );
        }

        return <span key={`${part}-${index}`}>{part}</span>;
      })}
    </span>
  );
}