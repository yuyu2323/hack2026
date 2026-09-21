"""영업 도메인의 전송 형식·조회 범위·멱등 처리를 모은다."""
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
import hashlib
import json
import re
from uuid import UUID, uuid4
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from server.core.db import utcnow, as_utc
from server.core.errors import ApiError
from server.core.permissions import accessible_store_ids, require_store_access, require_business
from server.accounts.models import Account
from server.stores.models import Store, Region, Category
from server.operations.models import AuditEvent
from server.analysis_jobs.models import IdempotencyRecord

BUSINESS_ROLES = ('store_owner', 'ofc', 'regional', 'hq')
MANAGER_ROLES = ('ofc', 'regional', 'hq')

class InputModel(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)

class BusinessFilter(InputModel):
    region_id: UUID | None = None
    store_id: UUID | None = None
    category_id: UUID | None = None
    date_from: date | None = None
    date_to: date | None = None
    is_active: bool | None = None


def encode(value):
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, datetime):
        return as_utc(value).isoformat().replace('+00:00', 'Z')
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, dict):
        return {key: encode(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [encode(item) for item in value]
    return value


def fields(row, names):
    return {name: encode(getattr(row, name)) for name in names.split()}


def page(items, number=1, size=20):
    if number < 1 or size < 1 or size > 100:
        raise ApiError(422, 'VALIDATION_ERROR', '페이지 범위를 확인해 주세요.')
    return {'items': items[(number - 1) * size:number * size], 'total': len(items), 'page': number, 'page_size': size}


def active_category(db, category_id):
    category = db.get(Category, category_id)
    if category is None:
        raise ApiError(404, 'NOT_FOUND', '카테고리를 찾을 수 없습니다.')
    if not category.is_active:
        raise ApiError(422, 'INACTIVE_TARGET', '비활성 카테고리에는 새로 등록할 수 없습니다.')
    return category


def scoped_stores(db, account, filters):
    require_business(account)
    ids = accessible_store_ids(db, account)
    if filters.store_id:
        require_store_access(db, account, filters.store_id)
    if filters.region_id:
        region = db.get(Region, filters.region_id)
        if region is None or (account.role != 'hq' and not db.scalar(select(Store.id).where(Store.id.in_(ids), Store.region_id == filters.region_id).limit(1))):
            raise ApiError(404, 'NOT_FOUND', '조회할 지역을 찾을 수 없습니다.')
    if filters.category_id and db.get(Category, filters.category_id) is None:
        raise ApiError(404, 'NOT_FOUND', '카테고리를 찾을 수 없습니다.')
    query = select(Store).where(Store.id.in_(ids))
    if filters.store_id:
        query = query.where(Store.id == filters.store_id)
    if filters.region_id:
        query = query.where(Store.region_id == filters.region_id)
    if filters.is_active is not None:
        query = query.where(Store.is_active == filters.is_active)
    return list(db.scalars(query.order_by(Store.name, Store.id)))


def period(filters):
    end = filters.date_to or utcnow().date()
    start = filters.date_from or end - timedelta(days=27)
    if end < start or (end - start).days > 365:
        raise ApiError(422, 'VALIDATION_ERROR', '조회 기간은 시작일 이후 최대 366일이어야 합니다.')
    return datetime.combine(start, datetime.min.time(), timezone.utc), datetime.combine(end + timedelta(days=1), datetime.min.time(), timezone.utc)


def audit(db, actor, action, target_type, target_id, reason, before=None, after=None, request_id=None):
    event = AuditEvent(actor_id=actor.id, action=action, target_type=target_type, target_id=target_id,
                       reason=reason, before_data=encode(before or {}), after_data=encode(after or {}),
                       outcome='succeeded', request_id=UUID(str(request_id)) if request_id else uuid4())
    db.add(event)
    return event


def request_hash(method, target, body, hashes=None):
    content = {'method': method, 'target': str(target), 'body': encode(body), 'images': hashes or []}
    return hashlib.sha256(json.dumps(content, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()


def lock_idempotency(db, account, operation, key, digest):
    if not key or not re.fullmatch(r'[A-Za-z0-9_.:-]{16,128}', key):
        raise ApiError(422, 'VALIDATION_ERROR', '유효한 Idempotency-Key가 필요합니다.')
    # 같은 계정의 변경만 짧게 직렬화해 첫 요청끼리의 중복 생성도 막는다.
    db.scalar(select(Account).where(Account.id == account.id).with_for_update())
    existing = db.scalar(select(IdempotencyRecord).where(IdempotencyRecord.account_id == account.id,
                         IdempotencyRecord.operation == operation, IdempotencyRecord.key == key))
    if existing and existing.request_hash != digest:
        raise ApiError(409, 'IDEMPOTENCY_CONFLICT', '같은 요청 키를 다른 입력에 사용할 수 없습니다.')
    return existing


def save_idempotency(db, account, operation, key, digest, resource_id, status):
    db.add(IdempotencyRecord(account_id=account.id, operation=operation, key=key, request_hash=digest,
                            resource_id=resource_id, response_status=status))


def metadata_json(text, schema):
    try:
        return schema.model_validate_json(text)
    except Exception as exc:
        raise ApiError(422, 'VALIDATION_ERROR', '입력 필드와 값의 형식을 확인해 주세요.') from exc
