import re


# ══════════════════════════════════════════════════════════════════════════════
#  HELPER UTILITIES
# ══════════════════════════════════════════════════════════════════════════════

def _first(pattern: str, text: str, group: int = 1, flags=re.I) -> str | None:
    """
    Convenience wrapper: run re.search, return the requested capture group,
    or None if no match. Keeps extraction lines short and readable.
    """
    m = re.search(pattern, text, flags)
    return m.group(group).strip() if m else None


def _clean_amount(raw: str) -> str:
    """Remove thousand-separator commas from a number string."""
    return raw.replace(",", "").strip()


# ══════════════════════════════════════════════════════════════════════════════
#  FIELD EXTRACTORS
#  Each function is responsible for exactly one field or group of fields.
#  They are called independently, so a failure in one never breaks another.
# ══════════════════════════════════════════════════════════════════════════════

def _extract_document_type(text: str) -> str | None:
    """
    Identifies the document type from common header labels.
    Covers: Tax Invoice, Proforma Invoice, Purchase Order,
            Credit Note, Debit Note, Receipt, Bill, Contract.
    """
    patterns = [
        r"\b(Tax\s+Invoice)\b",
        r"\b(Proforma\s+Invoice)\b",
        r"\b(Purchase\s+Order)\b",
        r"\b(Credit\s+Note)\b",
        r"\b(Debit\s+Note)\b",
        r"\b(Receipt)\b",
        r"\b(Bill\s+of\s+Supply)\b",
        r"\b(Invoice)\b",
        r"\b(Contract)\b",
        r"\b(Agreement)\b",
    ]
    for p in patterns:
        m = re.search(p, text, re.I)
        if m:
            return m.group(1).strip()
    return None


def _extract_invoice_number(text: str) -> str | None:
    """
    Matches invoice / document reference numbers.
    Patterns covered:
      - Invoice No: ABC/123/25-26
      - Invoice #: ABC-001
      - Bill No. 42
      - Reference No: REF-2025-001
      - PO No / PO Number
      - Order No
    """
    return _first(
        r"(?:Invoice\s*(?:No|Number|#)|Bill\s*No\.?|"
        r"Reference\s*No\.?|Ref\.?\s*No\.?|"
        r"PO\s*(?:No|Number)|Order\s*No\.?)"
        r"\s*[:\-#]?\s*([A-Z0-9][A-Z0-9\/\-\.]+)",
        text
    )


def _extract_date(text: str) -> str | None:
    """
    Extracts the primary document date.
    Formats covered:
      DD-Mon-YY       → 10-Jan-26
      DD-Mon-YYYY     → 10-January-2026
      DD/MM/YYYY      → 10/01/2026
      DD.MM.YYYY      → 10.01.2026
      YYYY-MM-DD      → 2026-01-10
      Month DD, YYYY  → January 10, 2026

    Anchors on common labels: Dated, Date, Invoice Date, Bill Date, Date of Issue.
    Falls back to scanning the full text for any date pattern.
    """
    labeled = _first(
        r"(?:Dated?|Invoice\s*Date|Bill\s*Date|Date\s*of\s*Issue|Date\s*of\s*Supply)"
        r"\s*[:\-]?\s*"
        r"(\d{1,2}[\-/\.]\w{2,9}[\-/\.]\d{2,4}"
        r"|\w{3,9}\s+\d{1,2},?\s+\d{4}"
        r"|\d{4}[\-/]\d{2}[\-/]\d{2})",
        text
    )
    if labeled:
        return labeled

    # Fallback: first standalone date found anywhere
    return _first(
        r"\b(\d{1,2}[\-/]\w{3,9}[\-/]\d{2,4}"
        r"|\d{1,2}/\d{1,2}/\d{4}"
        r"|\d{4}-\d{2}-\d{2})\b",
        text
    )


def _extract_gstin_list(text: str) -> list[str]:
    """
    Returns ALL GSTINs found in the document.
    Indian GSTIN format: 2-digit state code + 10-char PAN + 1 digit + Z + 1 char
    Pattern: 2 digits + 5 letters + 4 digits + 1 letter + 1 digit + Z + 1 alphanumeric
    """
    return re.findall(
        r"\b(\d{2}[A-Z]{5}\d{4}[A-Z]{1}\d{1}Z[A-Z0-9]{1})\b",
        text,
        re.I
    )


def _extract_pan(text: str) -> str | None:
    """PAN number: 5 letters + 4 digits + 1 letter."""
    return _first(r"\b([A-Z]{5}\d{4}[A-Z]{1})\b", text)


def _extract_seller(text: str) -> str | None:
    """
    Tries to find the seller/vendor/supplier name.
    Strategy:
      1. Look for a label like 'Seller:', 'Vendor:', 'Supplier:', 'From:'
      2. Look for company suffix keywords (Pvt. Ltd., LLP, Inc., Corp., Ltd.)
         appearing in the first 300 characters (usually the letterhead).
    """
    labeled = _first(
        r"(?:Seller|Vendor|Supplier|Issued\s*by|From)\s*[:\-]\s*(.+?)(?:\n|GSTIN|PAN|Address)",
        text
    )
    if labeled:
        return labeled

    # Heuristic: company name in first 300 chars (letterhead position)
    snippet = text[:300]
    company = _first(
        r"([A-Z][A-Za-z\s]+(?:Pvt\.?\s*Ltd\.?|LLP|Limited|Inc\.|Corp\.|Enterprises|Solutions|Services))",
        snippet,
        flags=re.I
    )
    return company


def _extract_buyer(text: str) -> str | None:
    """
    Tries to find the buyer/customer/client name.
    Strategy:
      1. Look for a label like 'Buyer (Bill to)', 'To:', 'Customer:', 'Consignee:'
      2. Capture the company name that follows.
    """
    return _first(
        r"(?:Buyer\s*\(?Bill\s*to\)?|Billed?\s*To|Customer\s*Name|"
        r"Consignee|Client|To)\s*[:\-]?\s*([A-Z][A-Za-z\s\.\,&]+?)(?:\s{2,}|\n|GSTIN|Plot|Address)",
        text
    )


def _extract_amounts(text: str) -> dict:
    """
    Extracts financial amounts.
    Covers:
      - Subtotal / Taxable Value
      - CGST, SGST, IGST, UTGST (any rate)
      - Total / Grand Total (anchored on ₹, Rs., INR, or Total label)
    """
    amounts = {}

    # Subtotal / taxable value
    amounts["subtotal"] = _first(
        r"(?:Sub\s*Total|Taxable\s*(?:Value|Amount)|Total\s*(?:before\s*tax|Taxable))"
        r"\s*[:\-]?\s*(?:₹|Rs\.?|INR)?\s*([0-9,]+\.\d{2})",
        text
    )
    if amounts["subtotal"]:
        amounts["subtotal"] = _clean_amount(amounts["subtotal"])

    # CGST — any rate
    cgst = _first(
        r"CGST\s*@?\s*\d+\.?\d*\s*%?\s*[:\-]?\s*(?:₹|Rs\.?|INR)?\s*([0-9,]+\.\d{2})",
        text
    )
    amounts["cgst"] = _clean_amount(cgst) if cgst else None

    # SGST — any rate
    sgst = _first(
        r"SGST\s*@?\s*\d+\.?\d*\s*%?\s*[:\-]?\s*(?:₹|Rs\.?|INR)?\s*([0-9,]+\.\d{2})",
        text
    )
    amounts["sgst"] = _clean_amount(sgst) if sgst else None

    # IGST — any rate
    igst = _first(
        r"IGST\s*@?\s*\d+\.?\d*\s*%?\s*[:\-]?\s*(?:₹|Rs\.?|INR)?\s*([0-9,]+\.\d{2})",
        text
    )
    amounts["igst"] = _clean_amount(igst) if igst else None

    # Total amount — multiple anchor patterns
    total = _first(
        r"(?:Grand\s*Total|Total\s*Amount|Net\s*Payable|Amount\s*Payable|Total\s*Due)"
        r"\s*[:\-]?\s*(?:₹|Rs\.?|INR)?\s*([0-9,]+\.\d{2})",
        text
    )
    if not total:
        # Fallback: ₹ symbol directly before a number
        total = _first(r"₹\s*([0-9,]+\.\d{2})", text)
    if not total:
        # Fallback: Rs. or INR before a number
        total = _first(r"(?:Rs\.?|INR)\s*([0-9,]+\.\d{2})", text)

    amounts["total_amount"] = _clean_amount(total) if total else None

    return amounts


def _extract_line_items(text: str) -> list[dict]:
    """
    Extracts line items from the document text.

    Two strategies run in sequence:

    Strategy A — Table row pattern (works when pdfplumber pipe-delimited the table):
      Looks for rows like:
        Description | HSN | Qty | Rate | Amount
      Identifies rows where one cell looks like an amount (digits.digits)

    Strategy B — Inline pattern (works on OCR text):
      Looks for lines that contain both a description-like phrase and
      a currency amount on the same line.
    """
    items = []

    # Strategy A: pipe-delimited table rows from pdfplumber
    # Format: cell1 | cell2 | cell3 | ... where last meaningful cell is an amount
    table_pattern = re.compile(
        r"([A-Za-z][A-Za-z0-9\s\(\)&,\.\-]+?)"   # description
        r"\s*\|\s*"
        r"([0-9]{4,})"                              # HSN/SAC code (4+ digits)
        r"(?:\s*\|\s*[^\|]+)?"                      # optional qty column
        r"(?:\s*\|\s*[^\|]+)?"                      # optional rate column
        r"\s*\|\s*"
        r"([0-9,]+\.\d{2})",                        # amount
        re.I
    )
    for m in table_pattern.finditer(text):
        name = m.group(1).strip()
        hsn = m.group(2).strip()
        amount = _clean_amount(m.group(3))
        if len(name) > 3:  # filter noise
            items.append({"name": name, "hsn_sac": hsn, "amount": amount})

    if items:
        return items

    # Strategy B: OCR inline — description followed by amount on same segment
    inline_pattern = re.compile(
        r"([A-Z][A-Za-z\s\(\)&,\.\-]{5,60}?)"     # description (5-60 chars)
        r"\s+"
        r"([0-9]{4,6})"                             # HSN/SAC (4-6 digits)
        r"\s+"
        r"(?:[0-9]+\.?[0-9]*\s+)?"                 # optional qty
        r"(?:[0-9,]+\.\d{2}\s+)?"                  # optional rate
        r"([0-9,]+\.\d{2})",                        # amount
        re.I
    )
    for m in inline_pattern.finditer(text):
        name = m.group(1).strip()
        hsn = m.group(2).strip()
        amount = _clean_amount(m.group(3))
        if len(name) > 3:
            items.append({"name": name, "hsn_sac": hsn, "amount": amount})

    return items


def _extract_order_reference(text: str) -> dict:
    """
    Extracts buyer order / purchase order reference number and date.
    Covers: Buyer's Order No., PO Number, Order Date, Dated.
    """
    ref = {}

    ref["order_number"] = _first(
        r"(?:Buyer['']?s?\s*Order\s*No\.?|Purchase\s*Order\s*(?:No\.?|Number)|PO\s*(?:No\.?|Number))"
        r"\s*[:\-]?\s*([A-Z0-9][A-Z0-9\-\.\/]+)",
        text
    )

    ref["order_date"] = _first(
        r"(?:Order\s*Date|PO\s*Date|Dated?)\s*[:\-]?\s*"
        r"(\d{1,2}[\-/\.]\w{2,9}[\-/\.]\d{2,4}"
        r"|\w{3,9}\s+\d{1,2},?\s+\d{4}"
        r"|\d{4}[\-/]\d{2}[\-/]\d{2})",
        text
    )

    return {k: v for k, v in ref.items() if v}  # omit None values


def _extract_period(text: str) -> dict:
    """
    Extracts service/invoice period and contract period if present.
    Common in AMC, subscription, or service-based invoices.
    """
    period = {}

    # Invoice / service period: "Invoice Period: 01/10/2025 to 31/12/2025"
    inv_period = _first(
        r"(?:Invoice\s*Period|Service\s*Period|Period\s*of\s*Service)"
        r"[-:\s]*"
        r"(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}\s*(?:to|–|-)\s*\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})",
        text
    )
    if inv_period:
        period["invoice_period"] = inv_period

    # Contract period: "Contract Period: 01/01/2025 to 31/12/2027"
    contract = _first(
        r"(?:Contract\s*Period|Agreement\s*Period)"
        r"[-:\s]*"
        r"(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}\s*(?:to|–|-|To)\s*\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})",
        text
    )
    if contract:
        period["contract_period"] = contract

    return period


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN EXTRACTION FUNCTION
# ══════════════════════════════════════════════════════════════════════════════

def extract_invoice_data(text: str) -> dict:
    """
    Orchestrates all field extractors and assembles the final output dictionary.

    Only fields that were successfully extracted are included.
    Fields that could not be found are omitted entirely (no null clutter).

    Works for:
      - Tax invoices (Indian GST format)
      - Proforma invoices
      - Purchase orders
      - Service invoices / AMC bills
      - Receipts and bills of supply
      - Any PDF where these fields appear in standard label-value format
    """
    data = {}

    # Document type
    doc_type = _extract_document_type(text)
    if doc_type:
        data["document_type"] = doc_type

    # Document / invoice number
    inv_no = _extract_invoice_number(text)
    if inv_no:
        data["invoice_number"] = inv_no

    # Primary date
    date = _extract_date(text)
    if date:
        data["invoice_date"] = date

    # Seller
    seller = _extract_seller(text)
    if seller:
        data["seller_name"] = seller

    # Buyer
    buyer = _extract_buyer(text)
    if buyer:
        data["buyer_name"] = buyer

    # GSTINs
    gstins = _extract_gstin_list(text)
    if len(gstins) >= 1:
        data["seller_gstin"] = gstins[0]
    if len(gstins) >= 2:
        data["buyer_gstin"] = gstins[1]

    # PAN
    pan = _extract_pan(text)
    if pan:
        data["pan"] = pan

    # Buyer order reference
    order_ref = _extract_order_reference(text)
    if order_ref:
        data.update(order_ref)

    # Service / contract periods
    period = _extract_period(text)
    if period:
        data.update(period)

    # Line items
    items = _extract_line_items(text)
    if items:
        data["line_items"] = items

    # Financial amounts
    amounts = _extract_amounts(text)
    for key, value in amounts.items():
        if value:
            data[key] = value

    return data
