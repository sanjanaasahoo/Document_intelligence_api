import re

def clean_text(text: str) -> str:
    """
    Normalize OCR output so regex extraction becomes easier.
    """
    text = text.replace("\x0c", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()