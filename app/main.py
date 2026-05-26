from fastapi import FastAPI, UploadFile, File, HTTPException
import shutil
import os

from app.ocr_service import extract_text
from app.cleaner import clean_text
from app.parser import extract_invoice_data

app = FastAPI(
    title="Document Intelligence API",
    description=(
        "Upload any PDF — invoice, bill, purchase order, receipt, contract — "
        "and receive only the important fields as structured JSON."
    ),
    version="2.0.0"
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/")
def root():
    return {
        "message": "Document Intelligence API is running.",
        "usage": "POST /parse-pdf with a PDF file to extract structured data."
    }


@app.post("/parse-pdf")
async def parse_pdf(file: UploadFile = File(...)):
    """
    Accepts a PDF upload of any type (scanned, text-based, or mixed).
    """
    # Validate file type
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    # Save file
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # Step 1: Extract raw text (auto-detects PDF type)
        raw_text, pdf_type = extract_text(file_path)

        # Step 2: Clean the text
        cleaned_text = clean_text(raw_text)

        # Step 3: Extract important fields
        extracted_data = extract_invoice_data(cleaned_text)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

    return {
        "status": "success",
        "pdf_type": pdf_type,
        "fields_found": len(extracted_data),
        "data": extracted_data
    }
