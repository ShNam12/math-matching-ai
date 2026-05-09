from infra.storage.r2_client import R2StorageClient


def main() -> None:
    storage = R2StorageClient()

    key = "test/hello.txt"
    url = storage.upload_bytes(
        key=key,
        content=b"Hello from DATN",
        content_type="text/plain",
    )

    print("Uploaded key:", key)
    print("Public URL:", url)


if __name__ == "__main__":
    main()
