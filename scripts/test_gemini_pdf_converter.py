import asyncio
from pathlib import Path

from modules.ingestion.pdf_processing.gemini_pdf_converter import (
    convert_pdf_to_markdown,
)


async def main() -> None:
    pdf_path = Path("D:\\2025.2\\DATN\\data\\samples\\sample.pdf")

    if not pdf_path.exists():
        raise FileNotFoundError(f"Missing sample PDF: {pdf_path}")

    markdown = await convert_pdf_to_markdown(
        filename=pdf_path.name,
        content=pdf_path.read_bytes(),
    )

    print("Markdown length:", len(markdown))
    print("Preview:")
    print(markdown[:2000])


if __name__ == "__main__":
    asyncio.run(main())