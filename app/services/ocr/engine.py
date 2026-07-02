from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory

from flask import current_app


@dataclass(frozen=True)
class OCRExtraction:
    text: str
    confidence_score: float | None
    language_codes: str


class EasyOCRReceiptReader:
    def __init__(self, languages: list[str] | None = None):
        self.languages = languages or ["en"]
        self._reader = None

    def extract_text(self, file_path: str, extension: str) -> OCRExtraction:
        image_paths = self._image_paths(file_path, extension)
        text_blocks = []
        confidences = []

        for image_path in image_paths:
            results = self._reader_instance().readtext(str(image_path), detail=1, paragraph=False)
            for result in results:
                if len(result) < 3:
                    continue
                text = str(result[1]).strip()
                confidence = float(result[2])
                if text:
                    text_blocks.append(text)
                    confidences.append(confidence)

        return OCRExtraction(
            text="
".join(text_blocks),
            confidence_score=_average(confidences),
            language_codes=",".join(self.languages),
        )

    def _reader_instance(self):
        if self._reader is None:
            try:
                import easyocr
            except ImportError as exc:
                raise RuntimeError("EasyOCR is not installed. Install project requirements before processing receipts.") from exc

            model_dir = current_app.config.get("EASYOCR_MODEL_DIR")
            self._reader = easyocr.Reader(
                self.languages,
                gpu=False,
                model_storage_directory=model_dir,
                verbose=False,
            )
        return self._reader

    def _image_paths(self, file_path: str, extension: str) -> list[Path]:
        if extension in {"jpg", "jpeg", "png"}:
            return [Path(file_path)]
        if extension == "pdf":
            return self._convert_pdf(file_path)
        raise ValueError("Unsupported receipt format for OCR processing.")

    def _convert_pdf(self, file_path: str) -> list[Path]:
        try:
            from pdf2image import convert_from_path
        except ImportError as exc:
            raise RuntimeError("PDF processing requires pdf2image. Install project requirements before uploading PDFs.") from exc

        temp_dir = TemporaryDirectory()
        pages = convert_from_path(file_path, dpi=180, fmt="png", output_folder=temp_dir.name)
        image_paths = []
        for index, page in enumerate(pages, start=1):
            image_path = Path(temp_dir.name) / f"page-{index}.png"
            page.save(image_path, "PNG")
            image_paths.append(image_path)

        return _TemporaryImagePaths(image_paths, temp_dir)


class _TemporaryImagePaths(list):
    def __init__(self, paths: list[Path], temp_dir: TemporaryDirectory):
        super().__init__(paths)
        self._temp_dir = temp_dir


def _average(values: list[float]) -> float | None:
    if not values:
        return None
    return round(sum(values) / len(values), 4)
