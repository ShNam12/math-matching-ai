---
name: update-trac-nghiem
description: Use this skill when working on the DATN project to convert the current AI Matching/free-response question system into a multiple-choice question bank with AI Matching, taxonomy classification, semantic search, symbolic solver validation, distractor generation, and Neuro-symbolic quality checks. Trigger when the user asks to implement, plan, review, test, or continue the "Update trắc nghiệm", "MCQ", "trắc nghiệm", "Neuro-symbolic", "MathBank integration", or "question generation" work in this repository.
---

# Update Trắc Nghiệm Skill

## Source Of Truth

Always read this design document before implementation:

```text
Plan/update/update_trac_nghiem.md
Treat it as the source of truth for phases, ordering, schemas, tests, and Definition of Done.
The target system is:
Hệ thống ngân hàng câu hỏi trắc nghiệm Toán học
tích hợp AI Matching, Semantic Search, Taxonomy Classification
và Neuro-symbolic Validation.
Repository Context
Current project modules:
modules/question_generation/
modules/question_quality/
modules/question_segmenter/
modules/question_classification/
modules/semantic_search/
modules/embeddings/
infra/db/
apps/api/v1/
apps/frontend/src/pages/
Legacy project:
MathBank-main/
Important legacy sources:
MathBank-main/backend/solvers.py
MathBank-main/backend/services.py
Useful legacy concepts:
SolverService
DistractorService
QuestionGenerationService.generate_batch
_validate_quality
ALL_SOLVERS
Only reuse useful logic. Do not merge the old app wholesale.
Core Principles
Prefer incremental migration over rewrite.
Keep old free-response data working while adding multiple-choice support.
Do not remove existing fields:
statement
solution
answer
formulas
subject
chapter
difficulty
skills
Add MCQ fields conservatively:
question_type
choices
correct_choice
validation_report
generation_method
solver_code
distractor_metadata
Use:
question_type = "free_response"
for old/self-contained questions.
Use:
question_type = "multiple_choice"
for MCQ questions.
Required Workflow
When implementing this update, follow the phases in Plan/update/update_trac_nghiem.md.
Default order:
1. Schema/dataclass/API support for MCQ
2. Database fields and migration
3. Repository/API response support
4. MCQ structural quality rules
5. MCQ distractor duplicate rules
6. MCQ generation prompt/parser
7. Save MCQ and embed choices
8. neuro_symbolic module
9. Port solver registry/executor from MathBank-main
10. Port distractor generation
11. Symbolic validator
12. Integrate symbolic validator into QuestionQualityService
13. Symbolic MCQ generator
14. API endpoints for symbolic MCQ generation
15. MCQ parser from documents
16. Convert free-response to MCQ
17. Search/embedding/hybrid matching support for MCQ
18. Frontend ProblemDetail support
19. Frontend GenVariants support
20. Frontend Search/QA/Dashboard/Analytics support
21. Review workflow
22. Evaluation dataset and evaluator
At the start of each task:
1. Identify the matching phase and step.
2. Inspect existing code before editing.
3. Preserve existing behavior and tests.
4. Implement the smallest useful step.
5. Add or update tests.
6. Run focused tests first.
7. Run broader regression tests when feasible.
Backend Rules
Use existing project patterns.
Prefer extending:
modules/question_generation/
modules/question_quality/
modules/question_segmenter/
modules/embeddings/
modules/semantic_search/
apps/api/v1/models/
apps/api/v1/endpoints/
infra/db/models.py
infra/db/repositories/questions.py
For Neuro-symbolic logic, create or use:
modules/neuro_symbolic/
Suggested files:
modules/neuro_symbolic/__init__.py
modules/neuro_symbolic/schemas.py
modules/neuro_symbolic/solver_registry.py
modules/neuro_symbolic/solver_executor.py
modules/neuro_symbolic/distractors.py
modules/neuro_symbolic/symbolic_validator.py
modules/neuro_symbolic/template_matcher.py
modules/neuro_symbolic/parameter_sampler.py
Do not directly import production logic from MathBank-main.
Port and adapt only the needed logic.
MCQ Data Contract
A generated or saved MCQ should support this shape:
{
  "question_type": "multiple_choice",
  "statement": "Tính tích phân ...",
  "choices": [
    {
      "key": "A",
      "text": "...",
      "latex": "...",
      "is_correct": false,
      "distractor_type": "sign_error",
      "rationale": "Sai do đổi dấu."
    },
    {
      "key": "B",
      "text": "...",
      "latex": "...",
      "is_correct": true,
      "distractor_type": null,
      "rationale": null
    }
  ],
  "correct_choice": "B",
  "answer": "...",
  "solution": "...",
  "formulas": [],
  "generation_method": "ai_symbolic",
  "solver_code": "INT_XN_EXP",
  "validation_report": {
    "can_save": true,
    "warnings": [],
    "blocking_issues": [],
    "symbolic_checks": []
  }
}
For compatibility:
answer
still stores the correct answer content.
correct_choice
stores the option key such as A, B, C, or D.
MCQ Quality Rules
A valid MCQ should satisfy:
Has question_type = multiple_choice
Has choices
Has valid keys A/B/C/D
Has exactly one correct choice
correct_choice exists in choices
No empty choice text
No duplicate choice key
No duplicate choice content
Distractors are not equivalent to the correct answer
If solver is available, correct answer matches symbolic result
Blocking issues must prevent save.
Warnings may allow save but must be included in validation_report.
Recommended quality issue codes:
mcq_missing_choices
mcq_invalid_choice_count
mcq_invalid_choice_key
mcq_duplicate_choice_key
mcq_missing_correct_choice
mcq_correct_choice_not_found
mcq_multiple_correct_choices
mcq_no_correct_choice_flagged
mcq_empty_choice_text
mcq_duplicate_choice_content
mcq_distractor_equals_correct_answer
mcq_all_choices_too_similar
symbolic_correct_answer_verified
symbolic_correct_answer_mismatch
symbolic_distractor_equals_correct
symbolic_distractor_duplicate
symbolic_parse_failed
solver_not_available
Symbolic Validation Rules
Use SymPy where possible.
Check:
correct answer equals solver result
distractors do not equal solver result
distractors are not equivalent to each other
solver failures are reported clearly
parse failures do not crash the pipeline
If no solver is available, return a warning:
solver_not_available
Do not block save solely because no solver exists, unless implementing symbolic-only generation.
Generation Rules
For AI MCQ generation:
Generate exactly 4 choices: A, B, C, D.
Generate exactly one correct choice.
Avoid "all of the above" and "none of the above" in MVP.
Use plausible distractors, not random nonsense.
Keep formula style consistent with the source question.
Return strict JSON.
For symbolic MCQ generation:
sample params
execute solver
render statement
render correct answer
generate distractors
shuffle choices
build solution
run quality service
return candidate
Frontend Rules
Important pages:
apps/frontend/src/pages/GenVariants.jsx
apps/frontend/src/pages/ProblemDetail.jsx
apps/frontend/src/pages/SemanticSearch.jsx
apps/frontend/src/pages/QARules.jsx
apps/frontend/src/pages/Dashboard.jsx
apps/frontend/src/pages/Analytics.jsx
MCQ display should include:
statement
A/B/C/D choices
correct choice for admin/review views
solution
taxonomy metadata
QA score
validation status
warnings/blocking issues
solver code if available
generation method
Preserve free-response rendering.
Testing Policy
Every implementation step must end with tests.
Backend command:
.venv/Scripts/python.exe -m pytest -q
Use focused tests when appropriate:
.venv/Scripts/python.exe -m pytest tests/modules/question_quality -q
.venv/Scripts/python.exe -m pytest tests/modules/question_generation -q
.venv/Scripts/python.exe -m pytest tests/api/test_generation_save_endpoint.py -q
Frontend commands:
cd apps/frontend
npm run lint
npm run build
If tests cannot be run, explain why and list what should be run next.
Definition Of Done
A step is done only when:
Implementation matches the relevant section in Plan/update/update_trac_nghiem.md
Existing behavior still works
New MCQ behavior has tests
No unrelated refactor is introduced
API/frontend changes are consistent
Quality rules prevent invalid MCQ saves
Reporting Format
When reporting progress, mention:
Current phase/step
Files changed
Tests added or updated
Tests run
Remaining risks or next step