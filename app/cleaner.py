import re


def clean_text(text: str) -> str:
    """
    Normalizes raw text from either OCR or pdfplumber so that
    regex patterns in parser.py can match reliably.

    Problems this fixes:
      - \x0c  : form feed character inserted at page breaks by OCR engines
      - \r    : carriage return from Windows-style line endings
      - \t    : tabs from table extraction
      - \s+   : multiple consecutive spaces/newlines collapsed to one space

    We preserve the pipe character | because extract_text_from_text_pdf
    uses it as a table cell delimiter that the parser can use.
    """
    text = text.replace("\x0c", " ")   # page break control character
    text = text.replace("\r", " ")     # carriage return
    text = text.replace("\t", " ")     # tabs
    text = re.sub(r"\s+", " ", text)   # collapse all whitespace
    return text.strip()
