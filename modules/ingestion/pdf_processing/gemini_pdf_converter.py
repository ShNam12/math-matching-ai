import tempfile
from pathlib import Path

from google import genai
from google.genai import types

from core.config.settings import settings


PDF_TO_MARKDOWN_PROMPT = """
Convert this PDF into clean Markdown.

Requirements:
- Preserve all meaningful content.
- Preserve headings, paragraphs, lists, tables, examples, and exercises.
- Preserve mathematical formulas using LaTeX.
- Use inline math as $...$.
- Use block math as $$...$$.
- Do not summarize.
- Do not omit content.
- Do not add explanations outside the converted document.
- Return only Markdown.
- Format question markers as plain text lines, for example: "Câu 1: ...".
- Do not wrap question markers in bold or italic markdown.
- Preserve multiple-choice options as separate lines: A. ..., B. ..., C. ...

""".strip()


def _create_gemini_client() -> genai.Client:
    return genai.Client(api_key=settings.gemini_api_key)


def _validate_pdf_input(filename: str, content: bytes) -> None:
    if not filename:
        raise ValueError("PDF filename is required")

    if not filename.lower().endswith(".pdf"):
        raise ValueError(f"Expected a PDF file, got: {filename}")

    if not content:
        raise ValueError("PDF content is empty")


def _extract_response_text(response: types.GenerateContentResponse) -> str:
    text = response.text or ""
    text = text.strip()

    if not text:
        raise ValueError("Gemini returned empty Markdown content")

    return text


async def convert_pdf_to_markdown(
    *,
    filename: str,
    content: bytes,
) -> str:
    _validate_pdf_input(filename, content)

    suffix = Path(filename).suffix or ".pdf"
    temp_path: str | None = None

    try:
        with tempfile.NamedTemporaryFile(
            suffix=suffix,
            delete=False,
        ) as temp_file:
            temp_file.write(content)
            temp_path = temp_file.name

        client = _create_gemini_client()

        uploaded_file = client.files.upload(
            file=temp_path,
            config={"mime_type": "application/pdf"},
        )

        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=[
                PDF_TO_MARKDOWN_PROMPT,
                uploaded_file,
            ],
        )

        return _extract_response_text(response)

    finally:
        if temp_path is not None:
            Path(temp_path).unlink(missing_ok=True)