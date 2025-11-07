# file: ai_extraction/gemini_client.py
import json
import os
import requests
from typing import Dict, Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from loguru import logger
from common.config import settings
from common.utils import normalize_whitespace
from ai_extraction.normalize import filter_to_schema  # new import

# --------------------------
# Gemini API endpoint (v1beta)
# --------------------------
GEMINI_ENDPOINT = (
    "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
)


class GeminiError(Exception):
    """Custom error class for Gemini-related issues."""
    pass


# --------------------------
# Helper functions
# --------------------------

def _load_json(path: str) -> Any:
    """Load JSON from disk safely."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# Load canonical schema & few-shot examples
CANONICAL = _load_json("ai_extraction/prompts/canonical_schema.json")
FEW_SHOTS = _load_json("ai_extraction/prompts/few_shots.json")


def _make_prompt(ocr_text: str, hints: Optional[Dict] = None) -> Dict:
    """
    Build the Gemini API prompt request with few-shot examples.
    Guides the model to return structured JSON following the canonical schema.
    """
    sys_rules = (
        "You are an expert document parser for admission and institutional forms. "
        "Return ONLY valid JSON — no explanations or text outside JSON. "
        "Use exactly these field names from the canonical schema. "
        "Each field must have 'value', 'confidence' (0–1), and 'rationale' (<=15 words). "
        "If a field is missing, leave 'value' empty and confidence=0. "
        "Be robust to OCR noise, formatting errors, and partial labels."
    )

    # Few-shot examples guide Gemini to consistent structure
    examples = FEW_SHOTS.get("examples", [])
    content = [
        {"role": "user", "parts": [{"text": sys_rules}]},
        {"role": "user", "parts": [{"text": "Canonical schema:\n" + json.dumps(CANONICAL, indent=2)}]},
    ]

    for ex in examples:
        content.append({"role": "user", "parts": [{"text": ex["input"]}]})
        content.append({"role": "model", "parts": [{"text": json.dumps(ex["output"], indent=2)}]})

    # Add current OCR text
    user_text = "OCR TEXT:\n" + normalize_whitespace(ocr_text)
    if hints:
        user_text += "\n\nHINTS:\n" + json.dumps(hints, indent=2)
    content.append({"role": "user", "parts": [{"text": user_text}]})

    return {"contents": content}


# --------------------------
# Main extraction logic
# --------------------------

@retry(
    reraise=True,
    stop=stop_after_attempt(settings.get("ai.max_retries", 3)),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    retry=retry_if_exception_type(GeminiError),
)
def extract_structured_data(ocr_text: str, hints: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Calls Gemini API to convert raw OCR text into structured JSON fields
    matching the canonical schema.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise GeminiError("❌ GEMINI_API_KEY missing in environment (.env file).")

    # Use full model ID for Gemini
    model = settings.get("ai.model", "models/gemini-1.5-flash-latest")
    url = GEMINI_ENDPOINT.format(model=model)

    payload = _make_prompt(ocr_text, hints)
    headers = {"Content-Type": "application/json"}
    params = {"key": api_key}

    try:
        resp = requests.post(url, params=params, headers=headers, data=json.dumps(payload), timeout=90)
    except requests.exceptions.RequestException as e:
        raise GeminiError(f"🌐 Network error calling Gemini API: {e}")

    if resp.status_code >= 400:
        logger.error("Gemini API error {}: {}", resp.status_code, resp.text[:1000])
        raise GeminiError(f"HTTP {resp.status_code}: {resp.text[:400]}")

    data = resp.json()

    # --------------------------
    # Extract model JSON response
    # --------------------------
    try:
        text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
        parsed = json.loads(text)
        logger.info("✅ Gemini extraction successful: {} fields parsed", len(parsed))

        # Filter output strictly to canonical schema
        canonical_fields = CANONICAL.get("fields", [])
        filtered = filter_to_schema(parsed, canonical_fields)

        # Validate output structure
        for field in canonical_fields:
            if field not in filtered:
                filtered[field] = {"value": "", "confidence": 0.0, "rationale": "missing"}

        return filtered

    except json.JSONDecodeError as e:
        logger.error("❌ Gemini returned invalid JSON: {}", e)
        raise GeminiError("Invalid JSON format returned by Gemini.")
    except KeyError as e:
        logger.error("❌ Unexpected response structure: {}", e)
        raise GeminiError("Unexpected API response format.")
    except Exception as e:
        logger.error("⚠️ Unknown parsing error: {}", e)
        raise GeminiError(str(e))
