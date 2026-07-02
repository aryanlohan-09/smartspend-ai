import json
import re

from flask import current_app

from app.services.ai.exceptions import ReceiptParsingError


_RECEIPT_SCHEMA_PROMPT = """
You are an expense receipt parser for a finance dashboard.
Extract the receipt data from OCR text and return only valid JSON.

Required JSON keys:
- merchant_name: string
- date: string or null, preferably YYYY-MM-DD when clear
- time: string or null, 24-hour HH:MM when clear
- total: number
- gst: number or null
- payment_method: one of Cash, Card, UPI, Wallet, Bank Transfer, Other, Unknown
- currency: three-letter ISO currency code, default INR when the receipt appears Indian
- receipt_number: string or null
- category: one of Food, Grocery, Shopping, Medical, Travel, Entertainment, Bills, Fuel, Other
- confidence_score: number between 0 and 1

Rules:
- Use null for missing optional fields.
- Do not guess a receipt number.
- Choose the largest final payable amount as total.
- Categorize based on merchant and purchased items.
- Return JSON only, with no markdown.

OCR text:
"""


class GeminiReceiptClient:
    def __init__(self, api_key: str | None = None, model_name: str | None = None):
        self.api_key = api_key
        self.model_name = model_name

    def parse_receipt_text(self, ocr_text: str) -> dict:
        api_key = self.api_key or current_app.config.get("GEMINI_API_KEY")
        model_name = self.model_name or current_app.config.get("GEMINI_MODEL")
        if not api_key:
            raise ReceiptParsingError("GEMINI_API_KEY is not configured.")
        if not ocr_text.strip():
            raise ReceiptParsingError("OCR text is empty and cannot be parsed.")

        try:
            import google.generativeai as genai
        except ImportError as exc:
            raise ReceiptParsingError("google-generativeai is not installed.") from exc

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(
            _RECEIPT_SCHEMA_PROMPT + ocr_text,
            generation_config={
                "temperature": 0.1,
                "response_mime_type": "application/json",
            },
        )
        return _parse_json_response(getattr(response, "text", ""))


def _parse_json_response(text: str) -> dict:
    cleaned = _strip_markdown_fence(text).strip()
    if not cleaned:
        raise ReceiptParsingError("Gemini returned an empty response.")
    try:
        payload = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise ReceiptParsingError("Gemini response was not valid JSON.") from exc
    if not isinstance(payload, dict):
        raise ReceiptParsingError("Gemini response must be a JSON object.")
    return payload


def _strip_markdown_fence(text: str) -> str:
    match = re.search(r"```(?:json)?\s*(.*?)```", text, flags=re.IGNORECASE | re.DOTALL)
    return match.group(1) if match else text
