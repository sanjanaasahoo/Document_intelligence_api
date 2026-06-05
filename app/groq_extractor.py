import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Initialize Groq client using your API key from .env
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


def extract_with_groq(text: str, missing_fields: list[str]) -> dict:
    """
    Sends cleaned document text to LLaMA 3 via Groq.
    Only asks for fields that regex could not find.
    
    Why LLaMA 3 via Groq:
    - Understands semantic meaning, not just patterns
    - Handles OCR noise and label variation naturally
    - Free tier is fast enough for document processing
    - Returns structured JSON reliably when prompted correctly
    """

    # Tell the LLM exactly which fields to find and how to respond
    prompt = f"""
You are a document data extraction assistant.
Read the following document text and extract ONLY these fields: {missing_fields}

Rules:
- Return ONLY a valid JSON object. No explanation, no markdown, no extra text.
- If a field genuinely cannot be found, set its value to null.
- For line_items, return a list of objects with keys: name, hsn_sac, amount.
- For amounts, return only the number as a string, no currency symbols.
- For dates, return exactly as written in the document.
- For GSTINs, return the 15-character alphanumeric code only.

Document text:
\"\"\"
{text[:4000]}
\"\"\"

Respond with JSON only.
"""

    try:
        response = client.chat.completions.create(
            model="llama3-8b-8192",   # fast, free, accurate enough for structured extraction
            messages=[
                {
                    "role": "system",
                    "content": "You are a precise document data extraction engine. You return only valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0,            # 0 = deterministic, no creativity, just extraction
            max_tokens=1000
        )

        raw = response.choices[0].message.content.strip()

        # Clean any accidental markdown code fences the LLM might add
        raw = raw.replace("```json", "").replace("```", "").strip()

        return json.loads(raw)

    except json.JSONDecodeError:
        # LLM returned something that isn't valid JSON — return empty
        return {}
    except Exception as e:
        # Groq API error — don't crash the whole pipeline
        print(f"Groq extraction failed: {e}")
        return {}