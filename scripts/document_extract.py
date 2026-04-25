"""Extract a text excerpt from a catalog document for the categorizer prompt.

The excerpt is meant to surface what a human glances at when shelving a
book: title page, front matter, table of contents, and the start of the
first chapter. The agent uses it together with web research to write the
auto-summary and pick a shelf and tags.

Supported formats:

  - PDF: text via pdfplumber, with an OCR fallback (pdftoppm + pytesseract)
    for scanned documents.
  - EPUB and HTML: plain text via pandoc.
  - Markdown and plain text: read directly.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

DEFAULT_MAX_CHARS = 12000
DEFAULT_PDF_PAGES = 30
DEFAULT_OCR_PAGES = 5
TRUNCATION_MARKER = "\n[truncated]"

PDF_EXTENSIONS = {"pdf"}
EPUB_EXTENSIONS = {"epub"}
HTML_EXTENSIONS = {"html", "htm", "mhtml"}
TEXT_EXTENSIONS = {"md", "markdown", "txt"}


def extract_document_text(
    document_path: Path,
    *,
    max_chars: int = DEFAULT_MAX_CHARS,
    pdf_pages: int = DEFAULT_PDF_PAGES,
    ocr_pages: int = DEFAULT_OCR_PAGES,
) -> str:
    extension = document_path.suffix.lower().lstrip(".")
    if extension in PDF_EXTENSIONS:
        text = _extract_pdf_text(document_path, pdf_pages)
        if not text.strip():
            text = _extract_pdf_via_ocr(document_path, ocr_pages)
    elif extension in EPUB_EXTENSIONS:
        text = _extract_via_pandoc(document_path, "epub")
    elif extension in HTML_EXTENSIONS:
        text = _extract_via_pandoc(document_path, "html")
        if not text.strip():
            text = _read_text_file(document_path)
    elif extension in TEXT_EXTENSIONS:
        text = _read_text_file(document_path)
    else:
        return ""

    text = text.strip()
    if len(text) > max_chars:
        text = text[:max_chars] + TRUNCATION_MARKER
    return text


def _extract_pdf_text(document_path: Path, max_pages: int) -> str:
    try:
        import pdfplumber
    except ImportError:
        return ""

    pieces: list[str] = []
    with pdfplumber.open(document_path) as pdf:
        for page in pdf.pages[:max_pages]:
            extracted = page.extract_text() or ""
            if extracted.strip():
                pieces.append(extracted)
    return "\n\n".join(pieces)


def _extract_pdf_via_ocr(document_path: Path, max_pages: int) -> str:
    pdftoppm = shutil.which("pdftoppm")
    if pdftoppm is None:
        return ""
    try:
        import pytesseract
        from PIL import Image
    except ImportError:
        return ""

    pieces: list[str] = []
    with tempfile.TemporaryDirectory() as raw_tmpdir:
        tmpdir = Path(raw_tmpdir)
        result = subprocess.run(
            [
                pdftoppm,
                "-r",
                "200",
                "-l",
                str(max_pages),
                str(document_path),
                str(tmpdir / "page"),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            return ""
        for image_path in sorted(tmpdir.glob("page-*")):
            try:
                with Image.open(image_path) as image:
                    pieces.append(pytesseract.image_to_string(image))
            except Exception:
                continue
    return "\n\n".join(pieces)


def _extract_via_pandoc(document_path: Path, source_format: str) -> str:
    pandoc = shutil.which("pandoc")
    if pandoc is None:
        return ""
    result = subprocess.run(
        [pandoc, "-f", source_format, "-t", "plain", str(document_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return ""
    return result.stdout


def _read_text_file(document_path: Path) -> str:
    try:
        return document_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return document_path.read_text(encoding="utf-8", errors="replace")
