# file: ai_extraction/gemini_client.py
import json
import os
import requests
from typing import Dict, Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from loguru import logger
from common.config import settings
from common.utils import normalize_whitespace

# --------------------------
# Gemini API endpoint (v1beta)
# --------------------------
# Use the full model ID, as required by the latest API.
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
    This guides the model to return structured JSON following the canonical schema.
    """
    sys_rules = (
        "You are an expert document parser for admission forms and identity forms. "
        "Always return JSON only — no explanations or text outside JSON. "
        "Each key must exist in the schema. "
        "Each field must have 'value', 'confidence' (0-1), and 'rationale' (max 15 words). "
        "Missing or uncertain fields should have an empty string and confidence=0. "
        "Be robust to OCR noise, abbreviations, and label variations."
    )

    # Few-shot examples help Gemini learn the expected JSON structure
    examples = FEW_SHOTS.get("examples", [])
    content = [
        {"role": "user", "parts": [{"text": sys_rules}]},
        {"role": "user", "parts": [{"text": "Canonical schema:\n" + json.dumps(CANONICAL, indent=2)}]},
    ]

    for ex in examples:
        content.append({"role": "user", "parts": [{"text": ex["input"]}]})
        content.append({"role": "model", "parts": [{"text": json.dumps(ex["output"], indent=2)}]})

    # Add user OCR text
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
        raise GeminiError("GEMINI_API_KEY missing in environment.")

    # Use full model ID for current Gemini version
    model = settings.get("ai.model", "models/gemini-1.5-flash-latest")
    url = GEMINI_ENDPOINT.format(model=model)

    payload = _make_prompt(ocr_text, hints)
    headers = {"Content-Type": "application/json"}
    params = {"key": api_key}

    try:
        resp = requests.post(url, params=params, headers=headers, data=json.dumps(payload), timeout=60)
    except requests.exceptions.RequestException as e:
        raise GeminiError(f"Network error calling Gemini API: {e}")

    if resp.status_code >= 400:
        logger.error("Gemini API error {}: {}", resp.status_code, resp.text[:2000])
        raise GeminiError(f"HTTP {resp.status_code}: {resp.text[:500]}")

    data = resp.json()

    # Extract model’s generated JSON from response
    try:
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        parsed = json.loads(text)
        logger.info("Gemini extraction successful: {} keys parsed", len(parsed))
        return parsed
    except Exception as e:
        logger.error("Failed to parse Gemini response: {}", e)
        raise GeminiError("Invalid JSON from Gemini model.")
