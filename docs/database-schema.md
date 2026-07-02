# Database Schema

SmartSpend AI uses SQLAlchemy models backed by MySQL. The schema separates authentication, uploaded receipt files, OCR output, structured expense data, and monthly AI insights.

## Tables

### users

Stores registered account information for Flask-Login.

| Column | Type | Notes |
| --- | --- | --- |
| id | Integer | Primary key |
| name | String(120) | Required display name |
| email | String(255) | Required, unique, indexed |
| password_hash | String(255) | Required bcrypt hash |
| is_active | Boolean | Required |
| last_login_at | DateTime | Nullable |
| created_at | DateTime | Required |
| updated_at | DateTime | Required |

### receipts

Tracks uploaded files and processing state.

| Column | Type | Notes |
| --- | --- | --- |
| id | Integer | Primary key |
| user_id | Integer | Foreign key to users |
| original_filename | String(255) | Browser-uploaded name |
| stored_filename | String(255) | Unique server filename |
| file_path | String(500) | Local or mounted storage path |
| file_mime_type | String(100) | Validated upload MIME type |
| file_size_bytes | Integer | Required |
| file_hash | String(64) | SHA-256 hash |
| status | Enum | uploaded, processing, processed, duplicate, failed |
| failure_reason | String(500) | Processing failure detail |
| duplicate_of_id | Integer | Optional self-reference |
| created_at | DateTime | Required |
| updated_at | DateTime | Required |

### ocr_results

Stores EasyOCR extraction output.

| Column | Type | Notes |
| --- | --- | --- |
| id | Integer | Primary key |
| receipt_id | Integer | One-to-one receipt link |
| raw_text | Text | OCR text |
| confidence_score | Numeric(5,4) | Optional OCR confidence |
| engine | String(80) | Defaults to EasyOCR |
| language_codes | String(120) | Defaults to en |
| created_at | DateTime | Required |
| updated_at | DateTime | Required |

### expenses

Stores Gemini-normalized receipt fields and the expense category.

| Column | Type | Notes |
| --- | --- | --- |
| id | Integer | Primary key |
| receipt_id | Integer | One-to-one receipt link |
| merchant_name | String(255) | Required, indexed |
| receipt_number | String(120) | Indexed |
| purchased_at | DateTime | Indexed |
| total_amount | Numeric(12,2) | Required, indexed |
| gst_amount | Numeric(12,2) | Nullable |
| currency | String(3) | ISO currency code |
| payment_method | Enum | Cash, Card, UPI, Wallet, Bank Transfer, Other, Unknown |
| category | Enum | Food, Grocery, Shopping, Medical, Travel, Entertainment, Bills, Fuel, Other |
| ai_confidence_score | Numeric(5,4) | Optional model confidence |
| structured_data | JSON | Full Gemini JSON payload |
| created_at | DateTime | Required |
| updated_at | DateTime | Required |

### ai_insights

Stores generated monthly summaries and saving suggestions.

| Column | Type | Notes |
| --- | --- | --- |
| id | Integer | Primary key |
| user_id | Integer | Foreign key to users |
| month | Date | First day of summarized month |
| summary | Text | Monthly spending summary |
| largest_category | String(80) | Highest spending category |
| spending_habits | Text | Behavior analysis |
| saving_suggestions | Text | Practical suggestions |
| model_name | String(120) | Gemini model used |
| created_at | DateTime | Required |
| updated_at | DateTime | Required |

## Duplicate Detection

Duplicate detection is supported with:

- `receipts.file_hash` for exact file duplicates.
- `expenses.merchant_name`, `expenses.total_amount`, and `expenses.receipt_number` for semantic receipt duplicates.
- `receipts.duplicate_of_id` to preserve the duplicate upload while linking it to the original receipt.
