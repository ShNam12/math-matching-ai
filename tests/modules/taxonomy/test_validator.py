import json
from copy import deepcopy

import pytest

from modules.taxonomy import (
    DEFAULT_TAXONOMY_PATH,
    TaxonomyValidationError,
    TaxonomyDefinition,
    load_taxonomy,
    validate_taxonomy,
)


@pytest.fixture
def taxonomy_data() -> dict:
    return json.loads(DEFAULT_TAXONOMY_PATH.read_text(encoding="utf-8"))


def load_modified_taxonomy(raw_data: dict) -> TaxonomyDefinition:
    return TaxonomyDefinition.model_validate(raw_data)


def first_problem_type(raw_data: dict) -> dict:
    return raw_data["chapters"][0]["topics"][0]["problem_types"][0]


def test_validate_default_taxonomy_builds_lookup_index() -> None:
    index = validate_taxonomy(load_taxonomy())

    node = index.get("GT1_C2_01_T03_Integration_By_Parts")

    assert node is not None
    assert node.display_name == "Tích phân từng phần"
    assert node.parent == "GT1_C2_01_Indefinite_Integrals"
    assert node.default_difficulty == "medium"


def test_every_problem_type_has_machine_readable_matching_data() -> None:
    index = validate_taxonomy(load_taxonomy())

    for problem_type in index.problem_types.values():
        assert problem_type.display_name.strip()
        assert problem_type.parent in index.topics
        assert problem_type.aliases
        assert problem_type.positive_signals
        assert problem_type.skills
        assert problem_type.default_difficulty in {"easy", "medium", "hard"}


def test_validator_rejects_duplicate_code(taxonomy_data) -> None:
    raw_data = deepcopy(taxonomy_data)
    duplicate = deepcopy(raw_data["chapters"][0]["topics"][0])
    raw_data["chapters"][0]["topics"].append(duplicate)
    raw_data["expected_counts"]["topics"] += 1
    raw_data["expected_counts"]["problem_types"] += len(
        duplicate["problem_types"]
    )
    taxonomy = load_modified_taxonomy(raw_data)

    with pytest.raises(TaxonomyValidationError, match="Duplicate taxonomy code"):
        validate_taxonomy(taxonomy)


def test_validator_rejects_invalid_parent(taxonomy_data) -> None:
    raw_data = deepcopy(taxonomy_data)
    first_problem_type(raw_data)["parent"] = "GT1_UNKNOWN_TOPIC"
    taxonomy = load_modified_taxonomy(raw_data)

    with pytest.raises(TaxonomyValidationError, match="has parent"):
        validate_taxonomy(taxonomy)


def test_validator_rejects_unknown_skill(taxonomy_data) -> None:
    raw_data = deepcopy(taxonomy_data)
    first_problem_type(raw_data)["skills"].append("unknown_skill")
    taxonomy = load_modified_taxonomy(raw_data)

    with pytest.raises(TaxonomyValidationError, match="Unknown skill"):
        validate_taxonomy(taxonomy)


def test_validator_rejects_unknown_confusable_code(
    taxonomy_data,
) -> None:
    raw_data = deepcopy(taxonomy_data)
    first_problem_type(raw_data)["confusable_with"].append("GT1_UNKNOWN")
    taxonomy = load_modified_taxonomy(raw_data)

    with pytest.raises(TaxonomyValidationError, match="confusable_with"):
        validate_taxonomy(taxonomy)


def test_validator_rejects_count_mismatch(taxonomy_data) -> None:
    raw_data = deepcopy(taxonomy_data)
    raw_data["expected_counts"]["problem_types"] += 1
    taxonomy = load_modified_taxonomy(raw_data)

    with pytest.raises(TaxonomyValidationError, match="counts"):
        validate_taxonomy(taxonomy)


def test_validator_rejects_missing_official_chapter(
    taxonomy_data,
) -> None:
    raw_data = deepcopy(taxonomy_data)
    removed_chapter = raw_data["chapters"].pop()
    raw_data["expected_counts"]["chapters"] -= 1
    raw_data["expected_counts"]["topics"] -= len(
        removed_chapter["topics"]
    )
    raw_data["expected_counts"]["problem_types"] -= sum(
        len(topic["problem_types"])
        for topic in removed_chapter["topics"]
    )
    taxonomy = load_modified_taxonomy(raw_data)

    with pytest.raises(TaxonomyValidationError, match="three official"):
        validate_taxonomy(taxonomy)
