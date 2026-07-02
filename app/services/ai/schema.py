from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation

from app.models.enums import ExpenseCategory, PaymentMethod


@dataclass(frozen=True)
class ParsedReceipt:
    merchant_name: str
    receipt_number: str | None
    purchased_at: datetime | None
    total_amount: Decimal
    gst_amount: Decimal | None
    currency: str
    payment_method: PaymentMethod
    category: ExpenseCategory
    confidence_score: Decimal | None
    structured_data: dict


def normalize_receipt_payload(payload: dict) -> ParsedReceipt:
    merchant_name = _required_text(payload, "merchant_name")
    total_amount = _required_decimal(payload, "total")
    gst_amount = _optional_decimal(payload.get("gst"))
    currency = str(payload.get("currency") or "INR").strip().upper()[:3]
    payment_method = _enum_value(PaymentMethod, payload.get("payment_method"), PaymentMethod.UNKNOWN)
    category = _enum_value(ExpenseCategory, payload.get("category"), ExpenseCategory.OTHER)
    confidence_score = _optional_decimal(payload.get("confidence_score"))

    normalized = dict(payload)
    normalized.update(
        {
            "merchant_name": merchant_name,
            "receipt_number": _optional_text(payload.get("receipt_number")),
            "date": _optional_text(payload.get("date")),
            "time": _optional_text(payload.get("time")),
            "total": str(total_amount),
            "gst": str(gst_amount) if gst_amount is not None else None,
            "currency": currency,
            "payment_method": payment_method.value,
            "category": category.value,
            "confidence_score": str(confidence_score) if confidence_score is not None else None,
        }
    )

    return ParsedReceipt(
        merchant_name=merchant_name,
        receipt_number=normalized["receipt_number"],
        purchased_at=_parse_purchased_at(normalized.get("date"), normalized.get("time")),
        total_amount=total_amount,
        gst_amount=gst_amount,
        currency=currency,
        payment_method=payment_method,
        category=category,
        confidence_score=confidence_score,
        structured_data=normalized,
    )


def _required_text(payload: dict, key: str) -> str:
    value = _optional_text(payload.get(key))
    if not value:
        raise ValueError(f"Missing required field: {key}")
    return value


def _optional_text(value) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _required_decimal(payload: dict, key: str) -> Decimal:
    value = _optional_decimal(payload.get(key))
    if value is None:
        raise ValueError(f"Missing required numeric field: {key}")
    return value


def _optional_decimal(value) -> Decimal | None:
    if value in (None, ""):
        return None
    try:
        return Decimal(str(value).replace(",", "")).quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"Invalid numeric value: {value}") from exc


def _enum_value(enum_type, value, default):
    if value is None:
        return default
    text = str(value).strip().lower()
    for item in enum_type:
        if item.value.lower() == text or item.name.lower() == text.replace(" ", "_"):
            return item
    return default


def _parse_purchased_at(date_value: str | None, time_value: str | None) -> datetime | None:
    if not date_value:
        return None

    date_text = date_value.strip()
    time_text = (time_value or "00:00").strip()
    candidates = [f"{date_text} {time_text}", date_text]
    formats = [
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d %H:%M:%S",
        "%d-%m-%Y %H:%M",
        "%d/%m/%Y %H:%M",
        "%m/%d/%Y %H:%M",
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%m/%d/%Y",
    ]
    for candidate in candidates:
        for fmt in formats:
            try:
                return datetime.strptime(candidate, fmt)
            except ValueError:
                continue
    return None
