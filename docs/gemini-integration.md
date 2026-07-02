# Gemini Integration

Module 6 converts OCR text into structured expense records with Google Gemini. The integration is implemented as a service layer so routes stay thin and parsing logic remains testable.

## Flow

1. EasyOCR extracts raw text.
2. `GeminiReceiptClient` sends a strict JSON-only prompt to Gemini.
3. `normalize_receipt_payload` validates and normalizes the response.
4. `ExpenseAIService` persists an `Expense` row.
5. Semantic duplicates are detected with merchant, total amount, and receipt number.

## Extracted Fields

- Merchant name
- Date
- Time
- Total
- GST
- Payment method
- Currency
- Receipt number
- Category
- Confidence score

## Categories

Food, Grocery, Shopping, Medical, Travel, Entertainment, Bills, Fuel, and Other.

## Configuration

Set these environment variables locally and on Render:

- `GEMINI_API_KEY`
- `GEMINI_MODEL`

The default model value in `.env.example` is `gemini-1.5-flash`.
