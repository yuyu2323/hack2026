"""권한 범위 안에서 불변 기준 버전과 Reference 계보를 관리한다."""
from uuid import uuid4
from sqlalchemy import select, or_
from server.core.errors import ApiError
from server.core.permissions import accessible_store_ids, require_store_access
from server.stores.models import Region, Store
from server.guidelines.models import Guideline, GuidelineVersion, ReferencePhoto
from server.submissions.storage import store_media, cleanup, photo_dto
from server.business_common import active_category, audit, fields, page, MANAGER_ROLES


def require_manager(account):
    if account.role not in MANAGER_ROLES:
        raise ApiError(403, 'FORBIDDEN', '영업 관리자 권한이 필요합니다.')


def can_read_guideline(db, account, item):
    if account.role == 'hq':
        return True
    ids = accessible_store_ids(db, account)
    if item.store_id:
        return item.store_id in ids
    if item.region_id:
        return item.region_id == account.region_id
    return item.level in ('HQ', 'CATEGORY')


def require_write_scope(db, account, level, region_id=None, store_id=None, category_id=None):
    require_manager(account)
    if category_id:
        active_category(db, category_id)
    if store_id:
        require_store_access(db, account, store_id, write=True)
    if region_id:
        region = db.get(Region, region_id)
        if not region or (account.role != 'hq' and region_id != account.region_id):
            raise ApiError(404, 'NOT_FOUND', '지역을 찾을 수 없습니다.')
        if not region.is_active:
            raise ApiError(422, 'INACTIVE_TARGET', '비활성 지역에는 새 기준을 등록할 수 없습니다.')
    permitted = account.role == 'hq' or (account.role == 'regional' and (store_id or (level == 'REGION' and region_id == account.region_id))) or (account.role == 'ofc' and bool(store_id))
    if not permitted:
        raise ApiError(403, 'FORBIDDEN', '이 범위의 기준을 변경할 수 없습니다.')


def guideline_dto(db, item):
    current = db.scalar(select(GuidelineVersion).where(GuidelineVersion.guideline_id == item.id, GuidelineVersion.version == item.current_version))
    result = fields(item, 'id rule_key title level region_id store_id category_id is_active version current_version created_at updated_at')
    result['current'] = dict(version_id=str(current.id), **fields(current, 'version text change_reason created_at'))
    return result


def get_guideline(db, account, ident, lock=False):
    require_manager(account)
    query = select(Guideline).where(Guideline.id == ident)
    item = db.scalar(query.with_for_update().execution_options(populate_existing=True) if lock else query)
    if not item or not can_read_guideline(db, account, item):
        raise ApiError(404, 'NOT_FOUND', '진열 기준을 찾을 수 없습니다.')
    return item


def list_guidelines(db, account, store_id=None, region_id=None, category_id=None, level=None, is_active=None):
    require_manager(account)
    target_store = require_store_access(db, account, store_id) if store_id else None
    if region_id and account.role != 'hq' and region_id != account.region_id:
        raise ApiError(404, 'NOT_FOUND', '지역을 찾을 수 없습니다.')
    if target_store and region_id and target_store.region_id != region_id:
        return []
    selected_region = region_id or (target_store.region_id if target_store else None)
    region_stores = set(db.scalars(select(Store.id).where(Store.region_id == selected_region))) if selected_region else None
    rows = db.scalars(select(Guideline).order_by(Guideline.created_at.desc(), Guideline.id)).all()
    return [guideline_dto(db, row) for row in rows if can_read_guideline(db, account, row)
            and (not store_id or row.store_id in (None, store_id))
            and (not selected_region or (row.region_id in (None, selected_region)
                 and (row.store_id is None or row.store_id in region_stores)))
            and (not category_id or row.category_id in (None, category_id))
            and (not level or row.level == level) and (is_active is None or row.is_active == is_active)]


def create_guideline(db, account, data, request_id):
    require_write_scope(db, account, data.level, data.region_id, data.store_id, data.category_id)
    target = data.store_id or data.region_id or 'all'
    item = Guideline(id=uuid4(), rule_key=data.rule_key, title=data.title, level=data.level, region_id=data.region_id,
                     store_id=data.store_id, category_id=data.category_id, scope_key=f'{data.level}:{target}:{data.category_id or "all"}', created_by_id=account.id)
    db.add(item)
    db.flush()
    db.add(GuidelineVersion(id=uuid4(), guideline_id=item.id, version=1, text=data.text, change_reason=data.reason, created_by_id=account.id))
    audit(db, account, 'guideline.create', 'guideline', item.id, data.reason, after={'version': 1}, request_id=request_id)
    db.commit()
    return guideline_dto(db, item)


def revise_guideline(db, account, ident, data, request_id, status_only=False):
    item = get_guideline(db, account, ident, lock=True)
    require_write_scope(db, account, item.level, item.region_id, item.store_id, item.category_id)
    if item.version != data.version:
        raise ApiError(409, 'VERSION_CONFLICT', '진열 기준이 변경되었습니다. 최신 내용을 확인해 주세요.')
    before = {'version': item.current_version, 'is_active': item.is_active}
    if status_only:
        if item.is_active == data.is_active:
            return guideline_dto(db, item)
        item.is_active = data.is_active
    else:
        previous = db.scalar(select(GuidelineVersion).where(GuidelineVersion.guideline_id == item.id, GuidelineVersion.version == item.current_version))
        if previous.text == data.text and (data.title is None or data.title == item.title):
            return guideline_dto(db, item)
        item.current_version += 1
        if data.title is not None:
            item.title = data.title
        db.add(GuidelineVersion(id=uuid4(), guideline_id=item.id, version=item.current_version, text=data.text, change_reason=data.reason, created_by_id=account.id))
    item.version += 1
    audit(db, account, 'guideline.update', 'guideline', item.id, data.reason, before,
          {'version': item.current_version, 'is_active': item.is_active}, request_id)
    db.commit()
    return guideline_dto(db, item)


def reference_dto(db, row):
    return dict(**fields(row, 'id lineage_id version state_version category_id store_id caption is_active created_at'), photo=photo_dto(db, row.photo_id))


def get_reference(db, account, ident):
    require_manager(account)
    row = db.get(ReferencePhoto, ident)
    if not row or (row.store_id and row.store_id not in accessible_store_ids(db, account)):
        raise ApiError(404, 'NOT_FOUND', 'Reference를 찾을 수 없습니다.')
    return row


def list_references(db, account, category_id=None, store_id=None, include_inactive=False):
    require_manager(account)
    ids = accessible_store_ids(db, account)
    if store_id:
        require_store_access(db, account, store_id)
    query = select(ReferencePhoto).where(or_(ReferencePhoto.store_id.is_(None), ReferencePhoto.store_id.in_(ids)))
    if category_id:
        query = query.where(ReferencePhoto.category_id == category_id)
    if store_id:
        query = query.where(or_(ReferencePhoto.store_id.is_(None), ReferencePhoto.store_id == store_id))
    if not include_inactive:
        query = query.where(ReferencePhoto.is_active == True)
    return [reference_dto(db, row) for row in db.scalars(query.order_by(ReferencePhoto.created_at.desc(), ReferencePhoto.id))]


def create_reference(db, account, data, upload, request_id):
    require_write_scope(db, account, 'CATEGORY', store_id=data.store_id, category_id=data.category_id)
    paths = []
    try:
        media = store_media(db, account, upload, paths)
        ident = uuid4()
        row = ReferencePhoto(id=ident, lineage_id=ident, version=1, state_version=1, photo_id=media.id,
                             category_id=data.category_id, store_id=data.store_id, caption=data.caption, created_by_id=account.id)
        db.add(row)
        audit(db, account, 'reference.create', 'reference', ident, data.reason, after={'version': 1}, request_id=request_id)
        db.commit()
        return reference_dto(db, row)
    except Exception:
        db.rollback()
        cleanup(paths)
        raise


def change_reference(db, account, ident, data, request_id, upload=None, status_only=False):
    original = get_reference(db, account, ident)
    current = db.scalar(select(ReferencePhoto).where(ReferencePhoto.lineage_id == original.lineage_id).order_by(ReferencePhoto.version.desc()).limit(1).with_for_update().execution_options(populate_existing=True))
    if current.id != ident or current.state_version != data.state_version:
        raise ApiError(409, 'VERSION_CONFLICT', 'Reference가 변경되었습니다. 최신 항목을 다시 확인해 주세요.')
    require_write_scope(db, account, 'CATEGORY', store_id=current.store_id, category_id=current.category_id)
    if (status_only and current.is_active == data.is_active) or (not status_only and upload is None and current.caption == data.caption):
        return reference_dto(db, current)
    paths = []
    try:
        previous = {'version': current.version, 'is_active': current.is_active}
        if status_only:
            current.is_active = data.is_active
            current.state_version += 1
            result = current
        else:
            current.is_active = False
            current.state_version += 1
            db.flush()
            media_id = store_media(db, account, upload, paths).id if upload else current.photo_id
            result = ReferencePhoto(id=uuid4(), lineage_id=current.lineage_id, version=current.version + 1,
                                    state_version=1, photo_id=media_id, category_id=current.category_id,
                                    store_id=current.store_id, caption=data.caption, created_by_id=account.id)
            db.add(result)
        audit(db, account, 'reference.update', 'reference', result.id, data.reason, previous,
              {'version': result.version, 'is_active': result.is_active if status_only else True}, request_id)
        db.commit()
        return reference_dto(db, result)
    except Exception:
        db.rollback()
        cleanup(paths)
        raise
