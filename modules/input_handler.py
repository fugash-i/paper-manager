import re
import os
import fitz  # PyMuPDF

# Common DOI regex pattern
# Matches typical 10.xxxx/xxxxx format
DOI_PATTERN = r'\b(10\.\d{4,9}/[-._;()/:a-zA-Z0-9]+)\b'

def extract_doi_from_text(text: str) -> str | None:
    """
    Extract the first DOI found in the given text string.
    """
    match = re.search(DOI_PATTERN, text)
    if match:
        return match.group(1)
    return None

def extract_doi_from_pdf(pdf_path: str) -> str | None:
    """
    Extract DOI from the first page of a PDF file using PyMuPDF.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    try:
        doc = fitz.open(pdf_path)
        # Check first few pages, usually DOI is on the first page
        for page_num in range(min(2, len(doc))):
            page = doc.load_page(page_num)
            text = page.get_text()
            doi = extract_doi_from_text(text)
            if doi:
                doc.close()
                return doi
        doc.close()
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {e}")
        return None
    
    return None

def get_doi_from_input(input_value: str) -> str | None:
    """
    Determine if input is a file path or direct DOI string/URL, and return DOI.
    """
    # 1. If it's a file path
    if os.path.isfile(input_value) and input_value.lower().endswith('.pdf'):
        return extract_doi_from_pdf(input_value)
    
    # 2. If it's a direct string, try to find DOI
    return extract_doi_from_text(input_value)
