from pathlib import Path

from modules.question_segmenter import segment_questions


def main() -> None:
    markdown = Path("Plan/bttx.md").read_text(encoding="utf-8")
    result = segment_questions(markdown)

    print("Preamble:")
    print(result.preamble)
    print()
    print("Question count:", len(result.questions))

    for question in result.questions:
        print()
        print("=" * 60)
        print(f"{question.marker} {question.marker_number}")
        print("Sequence:", question.sequence_number)
        print()
        print("Statement:")
        print(question.statement)
        print()
        print("Solution:", question.solution)
        print("Answer:", question.answer)
        print("Formula count:", len(question.formulas))

        for formula in question.formulas:
            print(
                f"- [{formula.source}] "
                f"{formula.normalized_latex}"
            )


if __name__ == "__main__":
    main()