from pdf2image import convert_from_path
import pytesseract

# Tesseract OCR executable path
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\TessaractOCR\tesseract.exe"
)

def extract_text_from_scanned_pdf(pdf_path: str) -> str:
    """
    Convert scanned PDF pages into images,
    then apply OCR to extract text.
    """

    images = convert_from_path(
        pdf_path,
        poppler_path=r"C:\poppler-26.02.0\Library\bin"
    )

    full_text = ""

    for image in images:

        page_text = pytesseract.image_to_string(image)

        full_text += page_text + "\n"

    return full_text