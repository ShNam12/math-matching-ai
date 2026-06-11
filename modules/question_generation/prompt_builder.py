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

    return f"""
You are an expert mathematics question generator.

Generate {generation_count} new mathematics questions based on the source question.

Requirements:
- Keep the same mathematical topic.
- Do not copy the source statement verbatim.
- Keep the question solvable.
- Use clear LaTeX for formulas.
- Return valid JSON only.
- Do not wrap JSON in markdown fences.
- Escape every LaTeX backslash for JSON strings. For example, write "\\\\frac{{x}}{{2}}" instead of "\\frac{{x}}{{2}}".
- Do not use raw single backslashes in JSON string values.
- The JSON must have exactly this shape:
{{
  "items": [
    {{
      "statement": "question statement with LaTeX",
      "solution": "solution or null",
      "answer": "final answer or null",
      "difficulty": "easy|medium|hard or null",
      "skills": ["skill 1", "skill 2"]
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

Source question:
Marker: {source_question.marker} {source_question.marker_number}
Statement:
{source_question.statement}

Solution:
{source_question.solution or ""}

Answer:
{source_question.answer or ""}
""".strip()