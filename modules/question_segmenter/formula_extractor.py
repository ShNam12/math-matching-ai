import re

from modules.question_segmenter.schemas import ExtractedFormula, FormulaSource


FORMULA_RE = re.compile(
    r"""
    (?<!\\)\$\$(?P<display>.*?)(?<!\\)\$\$
    |
    (?<!\\)\$(?P<inline>[^\n$]+?)(?<!\\)\$
    |
    \\\[(?P<bracket>.*?)\\\]
    |
    \\\((?P<paren>.*?)\\\)
    """,
    re.DOTALL | re.VERBOSE,
)


def normalize_formula(formula: str) -> str:
    return re.sub(r"\s+", " ", formula).strip()


def extract_formulas(
    text: str | None,
    *,
    source: FormulaSource,
) -> list[ExtractedFormula]:
    if not text:
        return []

    formulas = []

    for match in FORMULA_RE.finditer(text):
        latex = next(
            value
            for value in match.groupdict().values()
            if value is not None
        ).strip()

        formulas.append(
            ExtractedFormula(
                latex=latex,
                normalized_latex=normalize_formula(latex),
                source=source,
            )
        )

    return formulas