# OCR Upload Pipeline

Module 5 adds secure receipt upload and OCR extraction. Uploaded files are validated, stored with UUID-based names, hashed with SHA-256, recorded in the database, and processed by EasyOCR.

## Supported Formats

- JPG
- JPEG
- PNG
- PDF

PDF uploads are converted to page images with `pdf2image` before OCR. Production environments that support PDF uploads must include Poppler in the runtime image.

## Processing Flow

1. The authenticated user uploads a receipt.
2. The file extension is validated against app config.
3. The file is streamed to disk while calculating SHA-256.
4. A `Receipt` row is created with processing status.
5. Exact file duplicates are detected by user and file hash.
6. EasyOCR extracts raw text and confidence scores.
7. An `OCRResult` row stores the raw OCR output.
8. The receipt status becomes processed, duplicate, or failed.

Gemini JSON normalization and expense categorization are intentionally handled in Module 6.
