from io import BytesIO
from pathlib import Path

from fastapi import HTTPException, UploadFile
from pypdf import PdfReader

DATA_DIR = Path(__file__).parent / "data"
RESUME_PATH = DATA_DIR / "resume.txt"

MAX_FILE_SIZE = 5 * 1024 * 1024


def get_resume_text():
    if not RESUME_PATH.exists():
        return ""

    return RESUME_PATH.read_text(encoding="utf-8")


async def save_resume(file: UploadFile):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Please upload a PDF resume."
        )

    contents = await file.read(MAX_FILE_SIZE + 1)

    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="Resume must be smaller than 5 MB."
        )

    try:
        reader = PdfReader(BytesIO(contents))

        text = "\n".join(
            page.extract_text() or ""
            for page in reader.pages
        ).strip()

    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Unable to read this PDF."
        )

    if not text:
        raise HTTPException(
            status_code=400,
            detail="No readable text found in the PDF."
        )

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Store extracted text locally, not the original PDF.
    RESUME_PATH.write_text(text, encoding="utf-8")

    return {
        "message": "Resume uploaded successfully",
        "filename": file.filename,
        "characters": len(text)
    }