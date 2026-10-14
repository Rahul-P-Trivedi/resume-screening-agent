"""
STEP 4 (tools): small helper functions the agent needs to do its job —
here, reading resumes and job descriptions off disk (.txt or .pdf).
"""

import os


def read_text_file(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def read_pdf_file(path: str) -> str:
    from PyPDF2 import PdfReader

    reader = PdfReader(path)
    text_parts = []
    for page in reader.pages:
        text_parts.append(page.extract_text() or "")
    return "\n".join(text_parts)


def read_document(path: str) -> str:
    """Read a .txt or .pdf file and return its plain text content."""
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        return read_pdf_file(path)
    return read_text_file(path)


def load_resumes(folder: str) -> dict:
    """
    Load every .txt / .pdf resume in `folder`.
    Returns {filename: resume_text}
    """
    resumes = {}
    if not os.path.isdir(folder):
        raise FileNotFoundError(f"Resume folder not found: {folder}")

    for fname in sorted(os.listdir(folder)):
        ext = os.path.splitext(fname)[1].lower()
        if ext not in (".txt", ".pdf"):
            continue
        full_path = os.path.join(folder, fname)
        try:
            resumes[fname] = read_document(full_path)
        except Exception as e:
            print(f"  [warn] Could not read {fname}: {e}")
    return resumes
