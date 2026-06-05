from fastapi import FastAPI, UploadFile, File, HTTPException
import shutil
import os

from app.ocr_service import extract_text
from app.cleaner import clean_text
from app.parser import extract_invoice_data
from app.groq_extractor import extract_with_groq

app = FastAPI(
    title="Document Intelligence API",
    description=(
        "Upload any PDF — invoice, purchase order, contract, receipt, report, form — "
        "and receive only the important fields as structured JSON."
    ),
    version="3.0.0"
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/")
def root():
    return {
        "message": "Document Intelligence API is running.",
        "usage": "POST /parse-pdf with any PDF file to extract structured data.",
        "version": "3.0.0 — Hybrid regex + Groq LLM extraction"
    }


@app.post("/parse-pdf")
async def parse_pdf(file: UploadFile = File(...)):
    """
    Two-layer hybrid extraction pipeline.

    Works for any PDF type — scanned or text-based.
    Works for any document type — invoice, contract, report, form, receipt, etc.

    Layer 1 — Regex parser (fast, offline, deterministic):
        Runs first. Reliable for fields that follow predictable patterns
        such as GSTINs, invoice numbers, totals anchored on rupee symbol.

    Layer 2 — Groq LLM / LLaMA 3 (semantic, context-aware):
        Runs after regex. Receives the full document text and what regex
        already found. Extracts everything important that regex missed.
        Works across any document format because it understands language,
        not just fixed patterns.

    Final output merges both layers. Regex fields take priority.
    Groq fills all gaps. Only found fields are returned — no nulls.
    """

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are accepted."
        )

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # STEP 1: Text extraction — auto-detects text vs scanned PDF
        raw_text, pdf_type = extract_text(file_path)

        # STEP 2: Clean the text
        cleaned_text = clean_text(raw_text)

        # Step 3: Layer 1 — Regex extraction
        regex_result = extract_invoice_data(cleaned_text)

        # Step 4: Decide which fields are still missing
        missing_fields = [
            key for key, value in regex_result.items()
            if value in (None, "", [])
        ]

        # Step 5: Layer 2 — Groq fills the missing ones
        groq_result = extract_with_groq(cleaned_text, missing_fields)
        for key, value in regex_result.items():
            if value is not None and value != "" and value != []:
                final_result[key] = value

        for key, value in groq_result.items():
            if key not in final_result:
                if value is not None and value != "" and value != []:
                    final_result[key] = value

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Processing failed: {str(e)}"
        )

    return {
        "status": "success",
        "pdf_type": pdf_type,
        "extraction_layers": {
            "regex_fields_found": len(regex_result),
            "groq_fields_added": len([
                k for k in groq_result
                if k not in regex_result
                and groq_result[k] not in (None, "", [])
            ])
        },
        "total_fields_found": len(final_result),
        "data": final_result
    }