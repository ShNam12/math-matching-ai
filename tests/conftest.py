import pytest

from infra.storage.r2_client import R2StorageClient


@pytest.fixture(autouse=True)
def mock_r2_upload(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_upload_bytes(
        self: R2StorageClient,
        *,
        key: str,
        content: bytes,
        content_type: str | None = None,
    ) -> None:
        return None

    monkeypatch.setattr(R2StorageClient, "upload_bytes", fake_upload_bytes)