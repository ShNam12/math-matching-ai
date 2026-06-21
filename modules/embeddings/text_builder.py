from infra.db.models import Question


def _choice_value(choice: object, field: str):
    if isinstance(choice, dict):
        return choice.get(field)

    return getattr(choice, field, None)


def _format_choice(choice: object) -> str:
    key = _choice_value(choice, "key") or "?"
    text = _choice_value(choice, "text") or ""
    latex = _choice_value(choice, "latex")
    is_correct = _choice_value(choice, "is_correct") is True

    value = str(text).strip()

    if latex:
        latex_text = str(latex).strip()
        if latex_text and latex_text != value:
            value = f"{value} | {latex_text}" if value else latex_text

    suffix = " (correct)" if is_correct else ""
    return f"- {key}: {value}{suffix}"


def build_question_embedding_text(question: Question) -> str:
    question_type = getattr(question, "question_type", "free_response")
    parts = [
        f"Marker: {question.marker} {question.marker_number}",
        f"Question type: {question_type}",
        f"Statement:\n{question.statement}",
    ]

    choices = getattr(question, "choices", [])

    if choices:
        parts.append(
            "Choices:\n"
            + "\n".join(
                _format_choice(choice)
                for choice in choices
            )
        )

    correct_choice = getattr(question, "correct_choice", None)

    if correct_choice:
        parts.append(f"Correct choice: {correct_choice}")

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

    taxonomy_lines = []

    metadata = [
        ("Subject", getattr(question, "subject", None)),
        (
            "Chapter",
            getattr(question, "chapter_name", None)
            or getattr(question, "chapter", None),
        ),
        ("Topic", getattr(question, "topic_name", None)),
        ("Problem type", getattr(question, "problem_type_name", None)),
        ("Difficulty", getattr(question, "difficulty", None)),
    ]

    for label, value in metadata:
        if value:
            taxonomy_lines.append(f"{label}: {value}")

    skills = getattr(question, "skills", [])
    if skills:
        taxonomy_lines.append(f"Skills: {', '.join(skills)}")

    if taxonomy_lines:
        parts.append("Taxonomy:\n" + "\n".join(taxonomy_lines))

    content = "\n\n".join(parts)

    return f"title: {question.marker} {question.marker_number} | text: {content}"


def build_formula_embedding_text(normalized_latex: str) -> str:
    return (
        "task: sentence similarity | query: "
        f"mathematical formula: {normalized_latex}"
    )
