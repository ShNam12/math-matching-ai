import re


def _normalize_formula_spaces(formula: str) -> str:
    return re.sub(r"\s+", " ", formula).strip()


def normalize_math_delimiters(text: str) -> str:
    text = re.sub(
        r"\\\((.*?)\\\)",
        lambda match: f"${_normalize_formula_spaces(match.group(1))}$",
        text,
        flags=re.DOTALL,
    )

    text = re.sub(
        r"\\\[(.*?)\\\]",
        lambda match: f"$$\n{_normalize_formula_spaces(match.group(1))}\n$$",
        text,
        flags=re.DOTALL,
    )

    return text