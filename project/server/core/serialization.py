"""공통 목록과 공개 기본 자료형 변환."""
from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import UUID
from sqlalchemy import select,func


def scalar(value):
    if isinstance(value,UUID): return str(value)
    if isinstance(value,datetime):
        if value.tzinfo is None: value=value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc).isoformat().replace('+00:00','Z')
    if isinstance(value,date): return value.isoformat()
    if isinstance(value,Decimal): return float(value)
    return value


def fields(row, names):
    return {name:scalar(getattr(row,name)) for name in names}


def paginate(db,query,page,page_size,serialize):
    total=db.scalar(select(func.count()).select_from(query.order_by(None).subquery()))
    rows=db.scalars(query.offset((page-1)*page_size).limit(page_size)).all()
    return {'items':[serialize(row) for row in rows],'total':total,'page':page,'page_size':page_size}
