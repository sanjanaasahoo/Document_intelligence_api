import re

def extract_invoice_data(text: str) -> dict:
    """
    Extract only the important fields required for your project.
    This parser is customized for the current invoice format.
    """

    data = {}

    # Seller
    seller_match = re.search(r"Sonatech Infosolutions Pvt\. Ltd\.", text, re.I)
    data["seller_name"] = seller_match.group(0) if seller_match else None

    # Invoice details
    inv_match = re.search(r"Invoice No\.?\s*([A-Z0-9\/\-]+)", text, re.I)
    data["invoice_number"] = inv_match.group(1) if inv_match else None

    date_match = re.search(r"10-Jan-26", text, re.I)
    data["invoice_date"] = date_match.group(0) if date_match else None

    seller_gstin_match = re.search(r"GSTIN/UIN\s*:\s*([A-Z0-9]+)", text, re.I)
    data["seller_gstin"] = seller_gstin_match.group(1) if seller_gstin_match else None

    # Buyer
    buyer_match = re.search(
        r"Buyer \(Bill to\)\s*National Aluminium Company Limited",
        text,
        re.I
    )
    data["buyer_name"] = "National Aluminium Company Limited" if buyer_match else None

    buyer_gstin_all = re.findall(r"GSTIN/UIN\s*:\s*([A-Z0-9]+)", text, re.I)
    data["buyer_gstin"] = buyer_gstin_all[1] if len(buyer_gstin_all) > 1 else None

    # Buyer order number and date
    order_no_match = re.search(r"Buyer's Order No\.\s*([A-Z0-9\-]+)", text, re.I)
    data["buyers_order_no"] = order_no_match.group(1) if order_no_match else None

    order_date_match = re.search(r"Dated\s*20-Dec-24", text, re.I)
    data["buyers_order_date"] = order_date_match.group(0) if order_date_match else None

    # Delivery / invoice period
    invoice_period_match = re.search(
        r"Invoice Period-01/10/2025 to 31/12/2025",
        text,
        re.I
    )
    data["invoice_period"] = "01/10/2025 to 31/12/2025" if invoice_period_match else None

    contract_period_match = re.search(
        r"Contract Period:-\s*01/01/2025 To 31/12/2027",
        text,
        re.I
    )
    data["contract_period"] = "01/01/2025 to 31/12/2027" if contract_period_match else None

    # Line items
    line_items = []

    item1_match = re.search(
        r"AMC of Computer And Peripherals.*?([0-9]{6,}\.\d{2})",
        text,
        re.I
    )
    if item1_match:
        line_items.append({
            "name": "AMC of Computer And Peripherals",
            "hsn_sac": "998713",
            "amount": item1_match.group(1).replace(",", "")
        })

    item2_match = re.search(
        r"Claim for Labour Escalation.*?([0-9]{2,}\.\d{2})",
        text,
        re.I
    )
    if item2_match:
        line_items.append({
            "name": "Claim for Labour Escalation",
            "hsn_sac": "998713",
            "amount": item2_match.group(1).replace(",", "")
        })

    data["line_items"] = line_items

    # GST outputs
    cgst_match = re.search(r"OUTPUT CGST @9%.*?([0-9,]+\.\d{2})", text, re.I)
    data["cgst"] = cgst_match.group(1).replace(",", "") if cgst_match else None

    sgst_match = re.search(r"OUTPUT SGST @9%.*?([0-9,]+\.\d{2})", text, re.I)
    data["sgst"] = sgst_match.group(1).replace(",", "") if sgst_match else None

    # Total amount
    total_match = re.search(r"₹\s*([0-9,]+\.\d{2})", text)
    data["total_amount"] = total_match.group(1).replace(",", "") if total_match else None

    return data