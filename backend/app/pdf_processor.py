import pdfplumber

def extract_text_from_pdf(filepath: str) -> str:
    """
    Extracts all text content from a PDF file.

    Args:
        filepath (str): The path to the PDF file.

    Returns:
        str: The concatenated text from all pages of the PDF.
             Returns an empty string if no text can be extracted.
    """
    pdf_text = ""
    try:
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    pdf_text += text + "\n"
    except Exception as e:
        print(f"Error extracting text from PDF {filepath}: {e}")
        # Optionally, re-raise or handle more gracefully
    return pdf_text
