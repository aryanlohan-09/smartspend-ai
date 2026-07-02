# SmartSpend AI

SmartSpend AI is an intelligent expense receipt scanner built as a production-quality Flask portfolio project. It uploads receipts, extracts OCR text, converts receipt text into structured expense data with Google Gemini, categorizes spending, detects duplicates, and presents the results in a clean SaaS dashboard.

## Tech Stack

- Python 3.12
- Flask with Blueprints
- SQLAlchemy and MySQL
- Flask-Login
- bcrypt
- EasyOCR
- Google Gemini API
- HTML, CSS, vanilla JavaScript
- Chart.js
- Render deployment with Docker

## Features

- Register, login, logout, hashed passwords, and session management
- Receipt upload for JPG, JPEG, PNG, and PDF
- EasyOCR text extraction
- Gemini JSON extraction for merchant, date, time, total, GST, payment method, currency, and receipt number
- Expense categorization into Food, Grocery, Shopping, Medical, Travel, Entertainment, Bills, Fuel, and Other
- Duplicate detection by file hash and semantic merchant/amount/receipt number matching
- Dashboard metrics and Chart.js visualizations
- Receipt history with search, filter, sort, and pagination
- Receipt details with OCR text and structured AI data
- Monthly insights and saving suggestions
- CSV and PDF export
- Render-ready Docker deployment

## Local Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
flask --app wsgi:app init-db
python run.py
```

Update `.env` with your MySQL connection and Gemini API key before processing receipts.

## Project Structure

```text
app/
  blueprints/      Flask route modules
  forms/           Request validation
  models/          SQLAlchemy models
  services/        OCR, AI, dashboard, export, and history logic
  static/          CSS, JavaScript, uploads
  templates/       Jinja templates
  utils/           CSRF, security headers, logging, errors
config/            Environment-driven settings
docs/              Architecture and deployment notes
scripts/           Local database helper scripts
```

## Render Deployment

The project includes `Dockerfile` and `render.yaml`. Configure `DATABASE_URL`, `GEMINI_API_KEY`, and other environment variables in Render, deploy the service, then run:

```bash
flask --app wsgi:app init-db
```

Full deployment notes are in `docs/deployment-render.md`.

## Module Status

1. Folder structure: complete
2. Database schema: complete
3. Flask architecture: complete
4. Authentication: complete
5. OCR upload pipeline: complete
6. Gemini integration: complete
7. Dashboard, history, insights, exports: complete
8. Deployment readiness: complete
