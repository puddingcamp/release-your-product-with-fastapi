from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import Select, select, literal_column, text, exists
from sqlalchemy.orm.attributes import InstrumentedAttribute
from typing import Any, Literal, Type
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import JSON
from sqlalchemy import cast, func


def exact_match_list_json(
    session: AsyncSession | Literal["sqlite", "postgresql"],
    attr: InstrumentedAttribute,
    value: Any,
    target_type: Type,
) -> Select:
    """JSON lookup하는 방식이 DBMS에 따라 다른 경우를 처리하기 위한 함수."""

    if isinstance(session, str):
        dialect_name = session
    else:
        dialect_name = session.get_bind().dialect.name

    is_sqlite = dialect_name == "sqlite"
    is_postgresql = dialect_name == "postgresql"

    if is_sqlite:
        return select(literal_column("1")).where(
            text(f"EXISTS (SELECT 1 FROM json_each({attr.key}) WHERE CAST(value AS TEXT) = :value)"),
        ).exists().params(value=str(value))
    
    if is_postgresql:
        # JSON 타입인 경우 JSONB로 캐스팅
        if isinstance(attr.type, JSON):
            attr = cast(attr, JSONB)

        # jsonb_array_elements_text를 사용하여 배열 요소를 펼침
        array_elements = func.jsonb_array_elements_text(attr).alias("element")

        # 특정 문자열과 일치하는 요소를 찾는 서브쿼리
        subquery = (
            select(1)
            .select_from(array_elements)
            .where(literal_column("element").cast(target_type) == value)
        )

        # EXISTS를 사용하여 최종 쿼리 생성
        return exists(subquery).select()
    
    raise ValueError(f"Unsupported database: {dialect_name}")
