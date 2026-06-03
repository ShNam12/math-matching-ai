from infra.db.models import Question


def build_question_embedding_text(question: Question) -> str:
    parts = [
        f"Marker: {question.marker} {question.marker_number}",
        f"Statement:\n{question.statement}",
    ]

    if question.solution:
        parts.append(f"Solution:\n{question.solution}")

    if question.answer:
        parts.append(f"Answer:\n{question.answer}")

    normalized_formulas = [
        formula["normalized_latex"]
        for formula in question.formulas
        if formula.get("normalized_latex")
    ]

    if normalized_formulas:
        parts.append(
            "Formulas:\n"
            + "\n".join(
                f"- {formula}"
                for formula in normalized_formulas
            )
        )

    content = "\n\n".join(parts)

    return f"title: {question.marker} {question.marker_number} | text: {content}"


def build_formula_embedding_text(normalized_latex: str) -> str:
    return (
        "task: sentence similarity | query: "
        f"mathematical formula: {normalized_latex}"
    )