from docx import Document


def extract_docx_text(file_path):
    doc = Document(file_path)

    paragraphs = [
        p.text
        for p in doc.paragraphs
        if p.text.strip()
    ]

    return "\n".join(paragraphs)