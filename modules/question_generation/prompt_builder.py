from infra.db.models import Question
from modules.question_generation.schemas import GenerationConstraints


def build_question_generation_prompt(
    *,
    source_question: Question,
    generation_count: int,
    constraints: GenerationConstraints,
) -> str:
    subject = constraints.subject or source_question.subject or "unknown"
    chapter = constraints.chapter or source_question.chapter or "unknown"
    difficulty = constraints.difficulty or source_question.difficulty or "same as source"
    skills = constraints.skills or source_question.skills

    skills_text = ", ".join(skills) if skills else "same as source"
    note_text = constraints.note.strip() if constraints.note else "none"

    return f"""
You are an expert mathematics question generator.

Generate {generation_count} new multiple-choice mathematics questions based on the source question.

Requirements:
- Keep the same mathematical topic.
- Do not copy the source statement verbatim.
- Keep the question solvable.
- Use clear LaTeX for formulas.
- Preserve the source LaTeX formula style whenever possible.
- Always generate exactly 4 choices with keys A, B, C, and D.
- Every choice must include non-empty "text".
- If the choice is a formula, set "text" to a readable plain/math expression and set "latex" to the LaTeX expression.
- Do not leave "text" empty when "latex" is present.
- Mark exactly one choice with "is_correct": true.
- Set "correct_choice" to the key of the only choice where "is_correct" is true.
- Make distractors plausible and use the same expression/formula style as the correct answer.
- Do not use "all of the above", "none of the above", "Tất cả đều đúng", or "Không đáp án nào đúng".
- Keep "answer" equal to the correct choice content, not only the choice key.
- Use "generation_method": "ai".
- Return valid JSON only.
- Do not wrap JSON in markdown fences.
- Escape every LaTeX backslash for JSON strings. For example, write "\\\\frac{{x}}{{2}}" instead of "\\frac{{x}}{{2}}".
- Do not use raw single backslashes in JSON string values.
- The JSON must have exactly this shape:
{{
  "items": [
    {{
      "question_type": "multiple_choice",
      "statement": "question statement with LaTeX",
      "choices": [
        {{
          "key": "A",
          "text": "choice text",
          "latex": "choice LaTeX or null",
          "is_correct": false,
          "rationale": "why this distractor is plausible or null"
        }},
        {{
          "key": "B",
          "text": "readable choice text, never empty",
          "latex": "choice LaTeX or null"
          "is_correct": true,
          "rationale": null
        }},
        {{
          "key": "C",
          "text": "choice text",
          "latex": "choice LaTeX or null",
          "is_correct": false,
          "rationale": "why this distractor is plausible or null"
        }},
        {{
          "key": "D",
          "text": "choice text",
          "latex": "choice LaTeX or null",
          "is_correct": false,
          "rationale": "why this distractor is plausible or null"
        }}
      ],
      "correct_choice": "B",
      "answer": "content of the correct choice",
      "solution": "solution or null",
      "difficulty": "easy|medium|hard or null",
      "skills": ["skill 1", "skill 2"],
      "generation_method": "ai"
    }}
  ]
}}

Target metadata:
- subject: {subject}
- chapter: {chapter}
- difficulty: {difficulty}
- skills: {skills_text}
- preserve_formula_style: {constraints.preserve_formula_style}
- avoid_duplicate: {constraints.avoid_duplicate}

Use the target metadata above for every generated question. If a user instruction
does not override taxonomy or difficulty, keep the generated questions aligned
with the source subject, chapter, difficulty, and skills.

Additional user instruction:
{note_text}

Source question:
Marker: {source_question.marker} {source_question.marker_number}
Statement:
{source_question.statement}

Solution:
{source_question.solution or ""}

Answer:
{source_question.answer or ""}
""".strip()


def build_convert_to_mcq_prompt(
    *,
    source_question: Question,
    generation_count: int,
    constraints: GenerationConstraints,
) -> str:
    subject = constraints.subject or source_question.subject or "unknown"
    chapter = constraints.chapter or source_question.chapter or "unknown"
    difficulty = constraints.difficulty or source_question.difficulty or "same as source"
    skills = constraints.skills or source_question.skills

    skills_text = ", ".join(skills) if skills else "same as source"
    note_text = constraints.note.strip() if constraints.note else "none"

    return f"""
You are an expert mathematics question converter.

Convert the free-response source question into {generation_count}
multiple-choice version(s).

Requirements:
- Preserve the same mathematical task and answer.
- You may lightly rephrase the statement, but do not change the required computation.
- Always generate exactly 4 choices with keys A, B, C, and D.
- Mark exactly one choice with "is_correct": true.
- Set "correct_choice" to the key of the only choice where "is_correct" is true.
- Make distractors plausible and use the same expression/formula style as the correct answer.
- Do not use "all of the above", "none of the above", "Tất cả đều đúng", or "Không đáp án nào đúng".
- Keep "answer" equal to the correct choice content, not only the choice key.
- Use "generation_method": "ai_convert".
- Return valid JSON only.
- Do not wrap JSON in markdown fences.
- Escape every LaTeX backslash for JSON strings. For example, write "\\\\frac{{x}}{{2}}" instead of "\\frac{{x}}{{2}}".
- Do not use raw single backslashes in JSON string values.
- The JSON must have exactly this shape:
{{
  "items": [
    {{
      "question_type": "multiple_choice",
      "statement": "converted question statement with LaTeX",
      "choices": [
        {{"key": "A", "text": "choice text", "latex": "choice LaTeX or null", "is_correct": false, "rationale": "why this distractor is plausible or null"}},
        {{"key": "B", "text": "choice text", "latex": "choice LaTeX or null", "is_correct": true, "rationale": null}},
        {{"key": "C", "text": "choice text", "latex": "choice LaTeX or null", "is_correct": false, "rationale": "why this distractor is plausible or null"}},
        {{"key": "D", "text": "choice text", "latex": "choice LaTeX or null", "is_correct": false, "rationale": "why this distractor is plausible or null"}}
      ],
      "correct_choice": "B",
      "answer": "content of the correct choice",
      "solution": "solution or null",
      "difficulty": "easy|medium|hard or null",
      "skills": ["skill 1", "skill 2"],
      "generation_method": "ai_convert"
    }}
  ]
}}

Target metadata:
- subject: {subject}
- chapter: {chapter}
- difficulty: {difficulty}
- skills: {skills_text}
- preserve_formula_style: {constraints.preserve_formula_style}

Additional user instruction:
{note_text}

Free-response source question:
Marker: {source_question.marker} {source_question.marker_number}
Statement:
{source_question.statement}

Solution:
{source_question.solution or ""}

Answer:
{source_question.answer or ""}
""".strip()
