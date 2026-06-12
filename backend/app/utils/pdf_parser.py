import fitz


def extract_pdf_text(file_path):
    text = []
    doc = fitz.open(file_path)
    
    for page in doc:
        text.append(page.get_text())
    doc.close()

    return "\n".join(text).strip()