import json
from pathlib import Path

from pydantic import ValidationError

from modules.taxonomy.schemas import TaxonomyDefinition
from modules.taxonomy.validator import TaxonomyIndex, validate_taxonomy


DEFAULT_TAXONOMY_PATH = (
    Path(__file__).resolve().parents[2]
    / "core"
    / "taxonomy"
    / "calculus_1_taxonomy.json"
)


class TaxonomyLoadError(ValueError):
    pass


def load_taxonomy(path: str | Path | None = None) -> TaxonomyDefinition:
    taxonomy_path = Path(path) if path is not None else DEFAULT_TAXONOMY_PATH

    try:
        raw_data = json.loads(taxonomy_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise TaxonomyLoadError(
            f"Taxonomy file was not found: {taxonomy_path}"
        ) from exc
    except OSError as exc:
        raise TaxonomyLoadError(
            f"Taxonomy file could not be read: {taxonomy_path}"
        ) from exc
    except json.JSONDecodeError as exc:
        raise TaxonomyLoadError(
            f"Taxonomy file contains invalid JSON: {taxonomy_path}"
        ) from exc

    try:
        return TaxonomyDefinition.model_validate(raw_data)
    except ValidationError as exc:
        raise TaxonomyLoadError(
            f"Taxonomy data does not match the required schema: {taxonomy_path}"
        ) from exc


def load_validated_taxonomy(
    path: str | Path | None = None,
) -> tuple[TaxonomyDefinition, TaxonomyIndex]:
    taxonomy = load_taxonomy(path)
    return taxonomy, validate_taxonomy(taxonomy)
