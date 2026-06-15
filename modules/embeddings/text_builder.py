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