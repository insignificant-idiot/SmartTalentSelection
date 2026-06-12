import os

from app.utils.pdf_parser import extract_pdf_text
from app.utils.docx_parser import extract_docx_text
from app.utils.image_parser import extract_image_text

def extract_text(file_path):
    extension = (
        os.path.splitext(file_path)[1].lower()
    )

    if extension == ".pdf":
        return extract_pdf_text(file_path)

    if extension == ".docx":
        return extract_docx_text(file_path)

    if extension in [".jpg", ".jpeg", ".png"]:
        return extract_image_text(file_path)

    raise ValueError(
        "Unsupported file format"
    )