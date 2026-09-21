"""업로드 사진을 디코딩하고 보호 저장소용 이미지로 정규화한다."""
import hashlib
from io import BytesIO
from pathlib import Path
import warnings
from PIL import Image, ImageOps, UnidentifiedImageError

LIMIT = 10 * 1024 * 1024


def normalize_image(content, filename, mime_type):
    suffix = Path(filename or '').suffix.lower()
    allowed = {'image/png': {'.png'}, 'image/jpeg': {'.jpg', '.jpeg'}}
    if not content or len(content) > LIMIT:
        raise ValueError('사진은 한 장당 10MiB 이하여야 합니다.')
    if mime_type not in allowed or suffix not in allowed[mime_type]:
        raise ValueError('JPEG 또는 PNG 사진의 확장자와 형식을 확인해 주세요.')
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('error', Image.DecompressionBombWarning)
            source = Image.open(BytesIO(content))
            expected = 'PNG' if mime_type == 'image/png' else 'JPEG'
            if source.format != expected:
                raise ValueError('신고한 형식과 실제 사진 형식이 다릅니다.')
            width, height = source.size
            if not (32 <= width <= 8192 and 32 <= height <= 8192) or width * height > 40000000:
                raise ValueError('사진 크기는 32~8192px, 전체 4천만 화소 이하여야 합니다.')
            source.load()
            picture = ImageOps.exif_transpose(source).convert('RGB')
            output = BytesIO()
            # EXIF·텍스트 메타데이터를 새 파일에 복사하지 않는다.
            picture.save(output, format=expected, **({'quality': 92} if expected == 'JPEG' else {}))
            normalized = output.getvalue()
            if len(normalized) > LIMIT:
                raise ValueError('정규화한 사진이 10MiB 한도를 초과했습니다.')
            thumb = picture.copy()
            thumb.thumbnail((480, 480))
            thumb_bytes = BytesIO()
            thumb.save(thumb_bytes, format='JPEG', quality=85)
            return {'content': normalized, 'thumbnail': thumb_bytes.getvalue(), 'mime_type': mime_type,
                    'width': picture.width, 'height': picture.height, 'byte_size': len(normalized),
                    'sha256': hashlib.sha256(normalized).hexdigest()}
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError, Image.DecompressionBombWarning) as exc:
        raise ValueError('사진 파일을 안전하게 읽을 수 없습니다.') from exc
