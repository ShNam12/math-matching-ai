import pytest
from fastapi.testclient import TestClient

import modules.ingestion.service as ingestion_module
from core.config.settings import settings

def test_upload_markdown_saves_normalized_content(client: TestClient) -> None:
    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "integration.md",
                b"#Title\r\n\r\nMath: \\(x^2   +   1\\)",
                "text/markdown",
            )
        },
    )

    assert response.status_code == 201
    document_id = response.json()["id"]

    markdown_response = client.get(f"/documents/{document_id}/markdown")

    assert markdown_response.status_code == 200
    assert markdown_response.json()["markdown_content"] == (
        "# Title\n\nMath: $x^2 + 1$\n"
    )


def test_upload_pdf_calls_converter(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_converter(*, filename: str, content: bytes) -> str:
        assert filename == "sample.pdf"
        assert content == b"%PDF sample"
        return "# Converted PDF"

    monkeypatch.setattr(
        ingestion_module,
        "convert_pdf_to_markdown",
        fake_converter,
    )

    response = client.post(
        "/documents/upload",
        files={"file": ("sample.pdf", b"%PDF sample", "application/pdf")},
    )

    assert response.status_code == 201
    document_id = response.json()["id"]

    markdown_response = client.get(f"/documents/{document_id}/markdown")

    assert markdown_response.status_code == 200
    assert markdown_response.json()["markdown_content"] == "# Converted PDF\n"


def test_upload_rejects_file_over_size_limit(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "max_upload_size_mb", 0)

    response = client.post(
        "/documents/upload",
        files={"file": ("large.md", b"x", "text/markdown")},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "File size must not exceed 0 MB"