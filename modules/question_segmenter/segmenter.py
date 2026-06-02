from modules.question_segmenter.formula_extractor import extract_formulas
from modules.question_segmenter.patterns import (
    QUESTION_START_RE,
    SECTION_MARKER_RE,
)
from modules.question_segmenter.schemas import (
    SegmentationResult,
    SegmentedQuestion,
)


def _get_section_name(section_marker: str) -> str:
    normalized = section_marker.casefold()

    if normalized == "đáp án":
        return "answer"

    return "solution"


def _split_question_sections(content: str) -> tuple[str, str | None, str | None]:
    sections: dict[str, list[str]] = {
        "statement": [],
        "solution": [],
        "answer": [],
    }

    current_section = "statement"

    for line in content.splitlines():
        match = SECTION_MARKER_RE.match(line)

        if match:
            current_section = _get_section_name(match.group("section"))
            rest = match.group("rest").strip()

            if rest:
                sections[current_section].append(rest)

            continue

        sections[current_section].append(line)

    statement = "\n".join(sections["statement"]).strip()
    solution = "\n".join(sections["solution"]).strip() or None
    answer = "\n".join(sections["answer"]).strip() or None

    return statement, solution, answer


def segment_questions(markdown: str) -> SegmentationResult:
    matches = list(QUESTION_START_RE.finditer(markdown))

    if not matches:
        return SegmentationResult(
            preamble=markdown.strip() or None,
            questions=[],
        )

    preamble = markdown[:matches[0].start()].strip() or None
    questions = []

    for index, match in enumerate(matches):
        next_start = (
            matches[index + 1].start()
            if index + 1 < len(matches)
            else len(markdown)
        )

        remaining_content = markdown[match.end():next_start]
        first_line_content = match.group("rest").strip()

        content = "\n".join(
            part
            for part in [first_line_content, remaining_content.strip()]
            if part
        )

        statement, solution, answer = _split_question_sections(content)

        formulas = [
            *extract_formulas(statement, source="statement"),
            *extract_formulas(solution, source="solution"),
            *extract_formulas(answer, source="answer"),
        ]

        questions.append(
            SegmentedQuestion(
                sequence_number=index + 1,
                marker=match.group("marker"),
                marker_number=match.group("number"),
                statement=statement,
                solution=solution,
                answer=answer,
                formulas=formulas,
            )
        )

    return SegmentationResult(
        preamble=preamble,
        questions=questions,
    )