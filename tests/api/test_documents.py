from fastapi.testclient import TestClient

def test_upload_and_fetch_document(
    client: TestClient,
    uploaded_document_ids: list[str],
) -> None:
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
    uploaded_document_ids.append(document_id)

    document_response = client.get(f"/documents/{document_id}")
    assert document_response.status_code == 200
    assert document_response.json()["id"] == document_id

    status_response = client.get(f"/documents/{document_id}/status")
    assert status_response.status_code == 200

    status_data = status_response.json()

    assert status_data["id"] == document_id
    assert status_data["status"] == "completed"
    assert status_data["message"] == "Document processed successfully"
    assert status_data["markdown_available"] is True
    assert status_data["error_message"] is None
    assert status_data["updated_at"]


def test_upload_rejects_unsupported_file_type(client: TestClient) -> None:
    response = client.post(
        "/documents/upload",
        files={"file": ("sample.txt", b"plain text", "text/plain")},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Only PDF and Markdown files are supported"


def test_get_unknown_document_returns_404(client: TestClient) -> None:
    response = client.get("/documents/missing")

    assert response.status_code == 404
    assert response.json()["detail"] == "Document not found"

