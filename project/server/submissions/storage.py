"""보호 미디어 파일과 DB 식별자의 연결을 관리한다."""
import hashlib
import json
import os
from pathlib import Path
from uuid import uuid4
from sqlalchemy import select, func, text
from server.core.config import get_settings
from server.core.errors import ApiError
from server.core.permissions import accessible_store_ids, require_business
from server.submissions.models import MediaAsset, MediaBlob, Submission, SubmissionPhoto, AnalysisContext
from server.guidelines.models import ReferencePhoto
from server.submissions.media import normalize_image, LIMIT
from server.business_common import fields


def store_media(db, account, upload, created_paths):
    raw = upload.file.read(LIMIT + 1)
    try:
        normalized = normalize_image(raw, upload.filename, upload.content_type)
    except ValueError as exc:
        code = 'FILE_TOO_LARGE' if len(raw) > LIMIT else 'UNSUPPORTED_MEDIA'
        raise ApiError(413 if len(raw) > LIMIT else 415, code, str(exc)) from exc
    source_kind = 'user_upload'
    manifest = Path(__file__).resolve().parents[2] / 'scripts/seed/manifest.json'
    if manifest.is_file():
        digest = hashlib.sha256(raw).hexdigest()
        entries = json.loads(manifest.read_text(encoding='utf-8')).get('images', [])
        if any(row.get('sha256') == digest for row in entries):
            source_kind = 'ai_generated_demo'
    ident = uuid4()
    extension = 'png' if normalized['mime_type'] == 'image/png' else 'jpg'
    storage_key = f'{ident}.{extension}'
    thumbnail_key = f'{ident}-thumbnail.jpg'
    write_media(db, [(storage_key, normalized['content']), (thumbnail_key, normalized['thumbnail'])], created_paths)
    row = MediaAsset(id=ident, storage_key=storage_key, thumbnail_key=thumbnail_key,
                     uploaded_by_id=account.id, source_kind=source_kind,
                     **{key: normalized[key] for key in ['sha256', 'mime_type', 'byte_size', 'width', 'height']})
    db.add(row)
    db.flush()
    return row


def cleanup(paths):
    for path in paths:
        path.unlink(missing_ok=True)


def photo_dto(db, media_id, position=1, photo_id=None):
    media = db.get(MediaAsset, media_id)
    result = fields(media, 'mime_type width height source_kind')
    result.update(id=str(photo_id or media.id), media_id=str(media.id), position=position,
                  url=f'/api/media/{media.id}', thumbnail_url=f'/api/media/{media.id}?variant=thumbnail')
    return result


def authorize_media(db, account, media_id):
    require_business(account)
    ids = accessible_store_ids(db, account)
    media = db.get(MediaAsset, media_id)
    if media is None:
        raise ApiError(404, 'NOT_FOUND', '사진을 찾을 수 없습니다.')
    linked = db.scalar(select(SubmissionPhoto.id).join(Submission, Submission.id == SubmissionPhoto.submission_id)
                       .where(Submission.store_id.in_(ids), SubmissionPhoto.media_id == media_id).limit(1))
    if linked:
        return media
    manager = account.role in ('ofc', 'regional', 'hq')
    refs = db.scalars(select(ReferencePhoto).where(ReferencePhoto.photo_id == media_id)).all()
    # 관리자의 현재 Reference 이력 범위와 보호 사진 범위를 일치시킨다.
    if any((ref.is_active or manager) and
           (ref.store_id in ids or (ref.store_id is None and (ids or manager))) for ref in refs):
        return media
    contexts = db.scalars(select(AnalysisContext).join(Submission).where(Submission.store_id.in_(ids))).all()
    if any(str(media_id) == reference['photo_id'] for context in contexts for reference in context.snapshot.get('references', [])):
        return media
    raise ApiError(404, 'NOT_FOUND', '사진을 찾을 수 없습니다.')


def protected_path(media, thumbnail=False):
    root = get_settings().media_root.resolve()
    path = (root / (media.thumbnail_key if thumbnail else media.storage_key)).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        raise ApiError(404, 'NOT_FOUND', '사진 파일을 찾을 수 없습니다.')
    return path


def write_media(db, entries, created_paths, *, allow_existing=False):
    """사진 본문과 썸네일을 동일 트랜잭션에 저장한다."""
    entries = list(entries)
    if get_settings().media_storage == 'database':
        # 합계 조회와 삽입을 묶어 저장 용량 경쟁을 막는다.
        if db.get_bind().dialect.name == 'postgresql':
            db.execute(text('SELECT pg_advisory_xact_lock(734289120)'))
        additions = []
        for key, content in entries:
            existing = db.get(MediaBlob, key)
            if existing is not None:
                if not allow_existing or existing.content != content:
                    raise ValueError('보호 이미지 내용이 변경되었습니다.')
            else:
                additions.append(MediaBlob(storage_key=key, content=content, byte_size=len(content)))
        used = db.scalar(select(func.coalesce(func.sum(MediaBlob.byte_size), 0)))
        if used + sum(row.byte_size for row in additions) > get_settings().media_database_max_bytes:
            raise ApiError(507, 'MEDIA_STORAGE_FULL', '사진 저장 용량이 가득 찼습니다. 관리자에게 문의해 주세요.')
        db.add_all(additions)
        db.flush()
        return
    root = get_settings().media_root
    root.mkdir(parents=True, exist_ok=True, mode=0o700)
    for key, content in entries:
        path = (root / key).resolve()
        if not path.is_relative_to(root.resolve()):
            raise ValueError('사진 저장 경로가 올바르지 않습니다.')
        if allow_existing and path.exists():
            if path.read_bytes() != content:
                raise ValueError('보호 이미지 내용이 변경되었습니다.')
            continue
        with os.fdopen(os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), 'wb') as file:
            file.write(content)
        created_paths.append(path)


def read_media(db, media, thumbnail=False):
    if get_settings().media_storage == 'database':
        key = media.thumbnail_key if thumbnail else media.storage_key
        blob = db.get(MediaBlob, key)
        if blob is None:
            raise ApiError(404, 'NOT_FOUND', '사진 파일을 찾을 수 없습니다.')
        content = bytes(blob.content)
    else:
        with protected_path(media, thumbnail).open('rb') as file:
            content = file.read(LIMIT + 1)
    if len(content) > LIMIT or (not thumbnail and (
            len(content) != media.byte_size or hashlib.sha256(content).hexdigest() != media.sha256)):
        raise ApiError(404, 'NOT_FOUND', '사진 파일을 확인할 수 없습니다.')
    return content
