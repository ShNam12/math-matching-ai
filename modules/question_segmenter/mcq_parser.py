import re
from dataclasses import dataclass

from modules.question_segmenter.schemas import SegmentedChoice


CHOICE_LINE_RE = re.compile(
    r"""
    ^[ \t]*
    (?:
        (?P<paren>\([A-F]\))
        |
        (?P<plain>[A-F])[\.)]
    )
    [ \t]+
    (?P<text>.*)
    $
    """,
    re.MULTILINE | re.VERBOSE,
)

ANSWER_LINE_RE = re.compile(
    r"""
    ^[ \t]*
    (?:\*\*|__)?
    (?:
        Đáp[ \t]+án
        |
        Dap[ \t]+an
        |
        Answer
    )
    (?:\*\*|__)?
    [ \t]*[:\-][ \t]*
    (?:\*\*|__)?
    (?P<answer>[A-F])
    (?:[\.)])?
    (?:\*\*|__)?
    [ \t]*$
    """,
    re.IGNORECASE | re.MULTILINE | re.VERBOSE,
)


@dataclass(frozen=True)
class ParsedMCQ:
    statement: str
    choices: list[SegmentedChoice]
    correct_choice: str | None = None
    answer: str | None = None


def _choice_key(raw_key: str) -> str:
    return raw_key.strip().strip("()").upper()


def _extract_answer(text: str | None) -> str | None:
    if not text:
        return None

    match = ANSWER_LINE_RE.search(text)
    if match:
        return match.group("answer").upper()

    stripped = text.strip().upper()
    if re.fullmatch(r"[A-F][\.)]?", stripped):
        return stripped[0]

    return None


def _strip_answer_lines(text: str) -> str:
    return ANSWER_LINE_RE.sub("", text).strip()


def parse_mcq(
    statement: str,
    *,
    answer: str | None = None,
) -> ParsedMCQ | None:
    cleaned_statement = _strip_answer_lines(statement)
    matches = list(CHOICE_LINE_RE.finditer(cleaned_statement))

    if len(matches) < 4:
        return None

    keys = [
        _choice_key(match.group("paren") or match.group("plain") or "")
        for match in matches
    ]

    valid_key_sets = [
        ["A", "B", "C", "D"],
        ["A", "B", "C", "D", "E", "F"],
    ]

    if keys not in valid_key_sets:
        return None
    
    stem = cleaned_statement[:matches[0].start()].strip()
    choices: list[SegmentedChoice] = []

    for index, match in enumerate(matches):
        next_start = (
            matches[index + 1].start()
            if index + 1 < len(matches)
            else len(cleaned_statement)
        )
        raw_text = cleaned_statement[match.start("text"):next_start].strip()

        if not raw_text:
            return None

        choices.append(
            SegmentedChoice(
                key=keys[index],
                text=raw_text,
            )
        )

    correct_choice = _extract_answer(statement) or _extract_answer(answer)

    if correct_choice is not None:
        choices = [
            SegmentedChoice(
                key=choice.key,
                text=choice.text,
                latex=choice.latex,
                is_correct=choice.key == correct_choice,
                distractor_type=choice.distractor_type,
                rationale=choice.rationale,
                metadata=choice.metadata,
            )
            for choice in choices
        ]

    return ParsedMCQ(
        statement=stem,
        choices=choices,
        correct_choice=correct_choice,
        answer=correct_choice or answer,
    )
