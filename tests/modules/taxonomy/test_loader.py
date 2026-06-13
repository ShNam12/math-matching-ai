import json
from pathlib import Path

import pytest

from modules.taxonomy import (
    DEFAULT_TAXONOMY_PATH,
    TaxonomyLoadError,
    load_taxonomy,
    load_validated_taxonomy,
)


def test_load_default_taxonomy() -> None:
    taxonomy = load_taxonomy()

    assert taxonomy.taxonomy_id == "calculus_1_hust_mi1111"
    assert taxonomy.version == "1.0.0"
    assert taxonomy.subject_display_name == "Giải tích 1"
    assert len(taxonomy.chapters) == 3
    assert len(taxonomy.skill_vocabulary) == 100


def test_load_and_validate_default_taxonomy() -> None:
    taxonomy, index = load_validated_taxonomy()

    assert taxonomy.expected_counts.chapters == 3
    assert len(index.chapters) == 3
    assert len(index.topics) == 16
    assert len(index.problem_types) == 128
    assert len(index.nodes) == 147


def test_load_taxonomy_rejects_missing_file(monkeypatch) -> None:
    def raise_missing_file(*args, **kwargs):
        raise FileNotFoundError

    monkeypatch.setattr(Path, "read_text", raise_missing_file)

    with pytest.raises(TaxonomyLoadError, match="was not found"):
        load_taxonomy("missing.json")


def test_load_taxonomy_rejects_invalid_json(monkeypatch) -> None:
    monkeypatch.setattr(Path, "read_text", lambda *args, **kwargs: "{not-json")

    with pytest.raises(TaxonomyLoadError, match="invalid JSON"):
        load_taxonomy("invalid.json")


def test_load_taxonomy_rejects_invalid_schema(monkeypatch) -> None:
    raw_data = json.loads(DEFAULT_TAXONOMY_PATH.read_text(encoding="utf-8"))
    raw_data.pop("taxonomy_id")
    monkeypatch.setattr(
        Path,
        "read_text",
        lambda *args, **kwargs: json.dumps(raw_data, ensure_ascii=False),
    )

    with pytest.raises(TaxonomyLoadError, match="required schema"):
        load_taxonomy("invalid-schema.json")
