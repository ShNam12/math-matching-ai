import re


QUESTION_START_RE = re.compile(
    r"""
    ^[ \t]*
    (?:\#{1,6}[ \t]*)?
    (?P<marker>Bài(?:[ \t]+tập)?|Câu(?:[ \t]+hỏi)?|Ví[ \t]+dụ)
    [ \t]+
    (?P<number>\d+(?:[.-]\d+)*)
    [ \t]*
    [.):\-]?
    [ \t]*
    (?P<rest>.*)
    $
    """,
    re.IGNORECASE | re.MULTILINE | re.VERBOSE,
)


SECTION_MARKER_RE = re.compile(
    r"""
    ^[ \t]*
    (?:\#{1,6}[ \t]*)?
    (?:\*\*|__)?
    (?P<section>
        Lời[ \t]+giải
        |Hướng[ \t]+dẫn[ \t]+giải
        |Giải
        |Đáp[ \t]+án
    )
        [ \t]*
    (?:
        [:\-][ \t]*(?:\*\*|__)?
        |
        (?:\*\*|__)?[ \t]*[:\-]?
    )
    [ \t]*
    (?P<rest>.*)
    $
    """,
    re.IGNORECASE | re.MULTILINE | re.VERBOSE,
)