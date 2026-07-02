import hashlib
import uuid
from dataclasses import dataclass
from pathlib import Path

from flask import current_app
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename


@dataclass(frozen=True)
class StoredFile:
    original_filename: str
    stored_filename: str
    file_path: str
    mime_type: str
    size_bytes: int
    sha256_hash: str
    extension: str


def validate_receipt_file(file: FileStorage) -> None:
    if file is None or not file.filename:
        raise ValueError("Choose a receipt file to upload.")

    extension = _extension(file.filename)
    allowed = current_app.config["ALLOWED_RECEIPT_EXTENSIONS"]
    if extension not in allowed:
        allowed_list = ", ".join(sorted(allowed))
        raise ValueError(f"Unsupported file type. Upload one of: {allowed_list}.")


def store_receipt_file(file: FileStorage) -> StoredFile:
    validate_receipt_file(file)

    original_filename = secure_filename(file.filename or "receipt")
    extension = _extension(original_filename)
    stored_filename = f"{uuid.uuid4().hex}.{extension}"
    upload_dir = Path(current_app.config["UPLOAD_FOLDER"])
    upload_dir.mkdir(parents=True, exist_ok=True)
    destination = upload_dir / stored_filename

    sha256 = hashlib.sha256()
    size_bytes = 0
    with destination.open("wb") as output_file:
        while True:
            chunk = file.stream.read(1024 * 1024)
            if not chunk:
                break
            size_bytes += len(chunk)
            sha256.update(chunk)
            output_file.write(chunk)

    if size_bytes == 0:
        destination.unlink(missing_ok=True)
        raise ValueError("The uploaded file is empty.")

    return StoredFile(
        original_filename=original_filename,
        stored_filename=stored_filename,
        file_path=str(destination),
        mime_type=file.mimetype or "application/octet-stream",
        size_bytes=size_bytes,
        sha256_hash=sha256.hexdigest(),
        extension=extension,
    )


def _extension(filename: str) -> str:
    return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
