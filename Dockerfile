FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1     PYTHONUNBUFFERED=1     PIP_NO_CACHE_DIR=1     EASYOCR_MODEL_DIR=/app/.easyocr

WORKDIR /app

RUN apt-get update     && apt-get install -y --no-install-recommends         build-essential         libglib2.0-0         libgl1         poppler-utils     && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip     && pip install -r requirements.txt

RUN mkdir -p /app/.easyocr     && python -c "import easyocr; easyocr.Reader(['en'], gpu=False, model_storage_directory='/app/.easyocr', verbose=False)"

COPY . .

RUN mkdir -p app/static/uploads logs /app/.easyocr

EXPOSE 10000

CMD ["gunicorn", "--bind", "0.0.0.0:10000", "--workers", "1", "--timeout", "300", "wsgi:app"]
