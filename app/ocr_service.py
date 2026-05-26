import pdfplumber
from pdf2image import convert_from_path
import pytesseract

# ─── PATH CONFIGURATION ────────────────────────────────────────────────────────
# These paths are specific to your Windows machine.
# Change them only if you reinstall Tesseract or Poppler elsewhere.

pytesseract.pytesseract.tesseract_cmd = r"C:\TessaractOCR\tesseract.exe"
POPPLER_PATH = r"C:\poppler-26.02.0\Library\bin"

# ─── PDF TYPE DETECTION ────────────────────────────────────────────────────────

def is_text_pdf(pdf_path: str) -> bool:
    """
    Opens the PDF with pdfplumber and checks whether real embedded text exists.

    A scanned PDF contains only images — pdfplumber will return None or
    an empty string for every page. A text-based PDF will return actual
    characters. We use a threshold of 30 characters to avoid false positives
    from PDFs that have a tiny bit of metadata text but are otherwise scanned.

    Returns:
        True  → PDF has embedded text  → use direct text extraction
        False → PDF is image-based     → use OCR pipeline
    """
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text and len(text.strip()) > 30:
                    return True
    except Exception:
        pass
    return False


# ─── TEXT PDF EXTRACTION ───────────────────────────────────────────────────────

def extract_text_from_text_pdf(pdf_path: str) -> str:
    """
    For digitally generated PDFs (invoices from Tally, SAP, Python, etc.)
    pdfplumber reads the embedded character data directly from the PDF
    internal structure — no images, no OCR, no noise.

    Also attempts to extract tables and appends their content as
    pipe-delimited rows so the parser can still find line item data.
    """
    full_text = ""

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:

            # Extract plain text
            text = page.extract_text()
            if text:
                full_text += text + "\n"

            # Extract tables (for line items, GST breakdowns, etc.)
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    # Filter out completely empty rows
                    cleaned_row = [cell if cell else "" for cell in row]
                    if any(cell.strip() for cell in cleaned_row):
                        full_text += " | ".join(cleaned_row) + "\n"

    return full_text


# ─── SCANNED PDF EXTRACTION ────────────────────────────────────────────────────

def extract_text_from_scanned_pdf(pdf_path: str) -> str:
    """
    For scanned PDFs (photographed or scanner-generated documents):

    1. pdf2image + Poppler renders each PDF page into a PIL image
    2. Tesseract OCR reads the pixel data and predicts text characters
    3. All page texts are concatenated into one string

    OCR output is inherently noisy — cleaner.py handles that next.
    """
    images = convert_from_path(pdf_path, poppler_path=POPPLER_PATH)

    full_text = ""
    for image in images:
        page_text = pytesseract.image_to_string(image)
        full_text += page_text + "\n"

    return full_text


# ─── UNIFIED ENTRY POINT ───────────────────────────────────────────────────────

def extract_text(pdf_path: str) -> tuple[str, str]:
    """
    Single function called by main.py.
    Detects PDF type, routes to the correct extractor, returns:
        - extracted text
        - pdf_type string ("text" or "scanned") for the API response
    """
    if is_text_pdf(pdf_path):
        return extract_text_from_text_pdf(pdf_path), "text"
    else:
        return extract_text_from_scanned_pdf(pdf_path), "scanned"
