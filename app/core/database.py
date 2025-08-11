from contextlib import contextmanager
from typing import Generator, List, Type, TypeVar

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Configs
from app.core.exception import DuplicateException, UnknownException

config = Configs()

engine = create_engine(config.DATABASE_URL, echo=True)
print("📌 DB Connection URL : ", config.DATABASE_URL)

SessionLocal = sessionmaker(bind=engine, class_=Session, expire_on_commit=False)

T = TypeVar("T", bound=BaseModel)


@contextmanager
def start_session():
    """PostgreSQL 연결 및 session 관리"""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close()


def get_db() -> Generator:
    """API 호출시 발동될 메소드"""
    with start_session() as session:
        yield session


def convert_rows_to_dict_list(query_result, dto_class: Type[T]) -> List[T]:
    """SQLAlchemy Rowresult -> 원하는 BaseModel List 형태로 형변환 해주는 메소드."""
    return [dto_class(**dict(row._mapping)) for row in query_result]


def convert_row_to_dict(query_result, dto_class: Type[T]):
    """SQLAlchemy Row result -> 원하는 BaseModel 형태로 형변환 해주는 메소드."""
    res_dict = dict(query_result._mapping)
    result = dto_class(**res_dict)
    return jsonable_encoder(result)


def convert_page_to_offset(size: int, page: int):
    """파라미터로 받은 paging 파라미터, offset 값으로 변환"""
    return (page - 1) * size


def get_order_by_clause(model, order_by: str, direction: str):
    """모델을 받아서 동적으로 정렬조건 반환하는 메소드."""
    try:
        order_column = getattr(model, order_by)
        if direction == "DESC":
            return order_column.desc()
        return order_column.asc()
    except AttributeError as e:
        raise e
