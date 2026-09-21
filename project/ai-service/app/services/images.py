import hashlib
import io
import warnings
from pathlib import PurePath

from PIL import Image, UnidentifiedImageError

from packages.review_contract.errors import ContractError


def validate_image(data: bytes, metadata, filename: str) -> bytes:
    values = metadata.model_dump() if hasattr(metadata, "model_dump") else metadata
    mime_type = values["mime_type"]
    expected_format = {"image/png": "PNG", "image/jpeg": "JPEG"}.get(mime_type)
    allowed_suffixes = {"image/png": {".png"}, "image/jpeg": {".jpg", ".jpeg"}}
    try:
        if not data or len(data) > 10 * 1024 * 1024:
            raise ValueError
        if expected_format is None or PurePath(filename).suffix.lower() not in allowed_suffixes[mime_type]:
            raise ValueError
        if hashlib.sha256(data).hexdigest() != values["sha256"]:
            raise ValueError
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(data)) as image:
                width, height = image.size
                if image.format != expected_format or not (32 <= width <= 8192 and 32 <= height <= 8192):
                    raise ValueError
                if width * height > 40_000_000:
                    raise ValueError
                image.verify()
            with Image.open(io.BytesIO(data)) as image:
                image.load()
    except (ValueError, KeyError, OSError, UnidentifiedImageError, Image.DecompressionBombWarning, Image.DecompressionBombError):
        raise ContractError("INVALID_IMAGE", "사진 파일을 확인할 수 없습니다.") from None
    return data
