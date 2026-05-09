from datetime import UTC, datetime
from hashlib import sha256

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from infra.db.models import Document


class DocumentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_document(
        self,
        *,
        filename: str,
        content_type: str | None,
        size_bytes: int,
        source_type: str,
    ) -> Document:
        document = Document(
            filename=filename,
            content_type=content_type,
            size_bytes=size_bytes,
            source_type=source_type,
            status="uploaded",
        )

        self.session.add(document)
        await self.session.commit()
        await self.session.refresh(document)

        return document

    async def get_document(self, document_id: str) -> Document | None:
        result = await self.session.execute(
            select(Document).where(Document.id == document_id)
        )
        return result.scalar_one_or_none()

    async def update_status(
        self,
        document: Document,
        status: str,
        error_message: str | None = None,
    ) -> Document:
        document.status = status
        document.error_message = error_message

        await self.session.commit()
        await self.session.refresh(document)

        return document

    async def save_r2_original(
        self,
        document: Document,
        *,
        r2_original_key: str,
        r2_original_url: str | None,
    ) -> Document:
        document.r2_original_key = r2_original_key
        document.r2_original_url = r2_original_url

        await self.session.commit()
        await self.session.refresh(document)

        return document

    async def save_markdown(
        self,
        document: Document,
        markdown_content: str,
    ) -> Document:
        document.markdown_content = markdown_content
        document.markdown_checksum = sha256(
            markdown_content.encode("utf-8")
        ).hexdigest()
        document.status = "completed"
        document.processed_at = datetime.now(UTC)
        document.error_message = None

        await self.session.commit()
        await self.session.refresh(document)

        return document

    async def mark_failed(
        self,
        document: Document,
        error_message: str,
    ) -> Document:
        document.status = "failed"
        document.error_message = error_message

        await self.session.commit()
        await self.session.refresh(document)

        return document
