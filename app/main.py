from fastapi import FastAPI, UploadFile, File
import shutil
import os

from app.ocr_service import extract_text_from_scanned_pdf
from app.cleaner import clean_text
from app.parser import extract_invoice_data

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/parse-pdf")
async def parse_pdf(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    raw_text = extract_text_from_scanned_pdf(file_path)
    cleaned_text = clean_text(raw_text)
    print(cleaned_text)
    extracted_data = extract_invoice_data(cleaned_text)

    return {
        "status": "success",
        "data": extracted_data
    }