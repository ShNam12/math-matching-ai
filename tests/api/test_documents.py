from fastapi.testclient import TestClient

from apps.api.main import app


client = TestClient(app)


def test_upload_and_fetch_document() -> None:
    upload_response = client.post(
        "/documents/upload",
        files={"file": ("sample.md", b"# Sample\n\nContent", "text/markdown")},
    )

    assert upload_response.status_code == 201
    uploaded = upload_response.json()
    assert uploaded["filename"] == "sample.md"
    assert uploaded["status"] == "uploaded"
    assert uploaded["size_bytes"] > 0

    document_id = uploaded["id"]

    document_response = client.get(f"/documents/{document_id}")
    assert document_response.status_code == 200
    assert document_response.json()["id"] == document_id

    status_response = client.get(f"/documents/{document_id}/status")
    assert status_response.status_code == 200
    assert status_response.json() == {
        "id": document_id,
        "status": "uploaded",
        "message": "Document uploaded and waiting for processing",
    }


def test_upload_rejects_unsupported_file_type() -> None:
    response = client.post(
        "/documents/upload",
        files={"file": ("sample.txt", b"plain text", "text/plain")},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Only PDF and Markdown files are supported"


def test_get_unknown_document_returns_404() -> None:
    response = client.get("/documents/missing")

    assert response.status_code == 404
    assert response.json()["detail"] == "Document not found"

