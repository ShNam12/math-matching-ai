import re
from dataclasses import dataclass

from modules.taxonomy.schemas import (
    ChapterNode,
    KnowledgeNode,
    ProblemTypeNode,
    TaxonomyDefinition,
    TopicNode,
)


CHAPTER_CODE_RE = re.compile(r"^GT1_C[1-3]_[A-Za-z0-9_]+$")
TOPIC_CODE_RE = re.compile(r"^GT1_C[1-3]_\d{2}_[A-Za-z0-9_]+$")
PROBLEM_TYPE_CODE_RE = re.compile(
    r"^GT1_C[1-3]_\d{2}_T\d{2}_[A-Za-z0-9_]+$"
)
EXPECTED_CHAPTER_CODES = {
    "GT1_C1_Differential_Calculus_One_Variable",
    "GT1_C2_Integral_Calculus_One_Variable",
    "GT1_C3_Multivariable_Functions",
}


class TaxonomyValidationError(ValueError):
    def __init__(self, issues: list[str]) -> None:
        self.issues = issues
        super().__init__("; ".join(issues))


@dataclass(frozen=True)
class TaxonomyIndex:
    nodes: dict[str, KnowledgeNode]
    chapters: dict[str, ChapterNode]
    topics: dict[str, TopicNode]
    problem_types: dict[str, ProblemTypeNode]

    def get(self, code: str) -> KnowledgeNode | None:
        return self.nodes.get(code)


def _has_blank(values: list[str]) -> bool:
    return any(not value.strip() for value in values)


def validate_taxonomy(taxonomy: TaxonomyDefinition) -> TaxonomyIndex:
    issues: list[str] = []
    nodes: dict[str, KnowledgeNode] = {}
    chapters: dict[str, ChapterNode] = {}
    topics: dict[str, TopicNode] = {}
    problem_types: dict[str, ProblemTypeNode] = {}

    def register(node: KnowledgeNode) -> None:
        if node.code in nodes:
            issues.append(f"Duplicate taxonomy code: {node.code}")
            return
        nodes[node.code] = node

        for field_name, values in (
            ("aliases", node.aliases),
            ("positive_signals", node.positive_signals),
            ("negative_signals", node.negative_signals),
            ("skills", node.skills),
            ("confusable_with", node.confusable_with),
        ):
            if _has_blank(values):
                issues.append(f"{node.code} contains a blank {field_name} value")

    for chapter in taxonomy.chapters:
        register(chapter)
        chapters[chapter.code] = chapter
        if not CHAPTER_CODE_RE.fullmatch(chapter.code):
            issues.append(f"Invalid chapter code format: {chapter.code}")

        for topic in chapter.topics:
            register(topic)
            topics[topic.code] = topic
            if not TOPIC_CODE_RE.fullmatch(topic.code):
                issues.append(f"Invalid topic code format: {topic.code}")
            if topic.parent != chapter.code:
                issues.append(
                    f"Topic {topic.code} has parent {topic.parent}, "
                    f"expected {chapter.code}"
                )

            for problem_type in topic.problem_types:
                register(problem_type)
                problem_types[problem_type.code] = problem_type
                if not PROBLEM_TYPE_CODE_RE.fullmatch(problem_type.code):
                    issues.append(
                        f"Invalid problem type code format: {problem_type.code}"
                    )
                if problem_type.parent != topic.code:
                    issues.append(
                        f"Problem type {problem_type.code} has parent "
                        f"{problem_type.parent}, expected {topic.code}"
                    )
                if not problem_type.aliases:
                    issues.append(
                        f"Problem type {problem_type.code} has no aliases"
                    )
                if not problem_type.positive_signals:
                    issues.append(
                        f"Problem type {problem_type.code} has no positive signals"
                    )
                if not problem_type.skills:
                    issues.append(
                        f"Problem type {problem_type.code} has no skills"
                    )

    if set(chapters) != EXPECTED_CHAPTER_CODES:
        issues.append("Taxonomy must contain the three official Calculus 1 chapters")

    actual_counts = (
        len(chapters),
        len(topics),
        len(problem_types),
    )
    expected_counts = (
        taxonomy.expected_counts.chapters,
        taxonomy.expected_counts.topics,
        taxonomy.expected_counts.problem_types,
    )
    if actual_counts != expected_counts:
        issues.append(
            "Taxonomy counts do not match expected_counts: "
            f"actual={actual_counts}, expected={expected_counts}"
        )

    if taxonomy.levels != ["chapter", "topic", "problem_type"]:
        issues.append("Taxonomy levels must be chapter, topic, problem_type")
    if taxonomy.difficulty_levels != ["easy", "medium", "hard"]:
        issues.append("Difficulty levels must be easy, medium, hard")

    skill_vocabulary = set(taxonomy.skill_vocabulary)
    if len(skill_vocabulary) != len(taxonomy.skill_vocabulary):
        issues.append("Skill vocabulary contains duplicate values")

    for node in nodes.values():
        for skill in node.skills:
            if skill not in skill_vocabulary:
                issues.append(f"Unknown skill {skill} in {node.code}")
        for related_code in node.confusable_with:
            if related_code not in nodes:
                issues.append(
                    f"Unknown confusable_with code {related_code} in {node.code}"
                )

    if issues:
        raise TaxonomyValidationError(issues)

    return TaxonomyIndex(
        nodes=nodes,
        chapters=chapters,
        topics=topics,
        problem_types=problem_types,
    )
