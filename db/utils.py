from datetime import datetime
from typing import TypeVar, Type, Any, AsyncGenerator

from sqlalchemy import DateTime, Update, Select, Delete, TextClause, Result, Insert, ColumnElement
from sqlalchemy import insert, update, select, delete, text
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, DataError
from sqlalchemy.orm import DeclarativeBase, declared_attr, Mapped, mapped_column

from db.exceptions import DatabaseException, logger
from db.session import AsyncSessionLocal

T = TypeVar("T", bound="Model")


class Base(DeclarativeBase):
    pass


class Manager:

    @classmethod
    async def create(cls: Type[T], **kwargs):
        async with AsyncSessionLocal() as session:
            try:
                stmt: Insert = insert(cls).values(**kwargs).returning(cls)
                result = await session.execute(stmt)
                await session.commit()
                return result.scalar_one()
            except (IntegrityError, DataError, SQLAlchemyError) as e:
                await session.rollback()
                cls._handle_db_error(e)

    @classmethod
    async def get_all(cls: Type[T], order_fields: list[ColumnElement[Any]] | None = None, limit: int = 100,
                      offset: int = 0):
        async with AsyncSessionLocal() as session:
            try:
                query: Select[Any] = select(cls).limit(limit).offset(offset)
                if order_fields:
                    query = query.order_by(*order_fields)
                results: Result[Any] = await session.execute(query)
                return results.scalars().all()
            except (SQLAlchemyError) as e:
                await session.rollback()
                cls._handle_db_error(e)

    @classmethod
    async def stream_all(
            cls: Type[T],
            order_fields: list[ColumnElement[Any]] | None = None,
            limit: int = 100,
            offset: int = 0
    ) -> AsyncGenerator[T, None]:
        async with AsyncSessionLocal() as session:
            try:
                query: Select[Any] = select(cls).limit(limit).offset(offset)
                if order_fields:
                    query = query.order_by(*order_fields)

                result = await session.stream_scalars(query)
                async for item in result:
                    yield item

            except SQLAlchemyError as e:
                await session.rollback()
                cls._handle_db_error(e)

    @classmethod
    async def get(cls: Type[T], **filter_):
        async with AsyncSessionLocal() as session:
            try:
                query: Select[Any] = select(cls).filter_by(**filter_)
                result: Result[Any] = await session.execute(query)
                return result.scalars().first()
            except(SQLAlchemyError) as e:
                await session.rollback()
                cls._handle_db_error(e)

    @classmethod
    async def get_filter(
            cls: Type[T], *filter_, order_by_fields: list[ColumnElement[Any]] | None = None,
            limit: int = 100, offset: int = 0
    ):
        async with AsyncSessionLocal() as session:
            try:
                query: Select[Any] = select(cls).where(*filter_).limit(limit).offset(offset)
                if order_by_fields:
                    query = query.order_by(*order_by_fields)
                result: Result[Any] = await session.execute(query)
                return result.scalars().all()
            except(SQLAlchemyError) as e:
                await session.rollback()
                cls._handle_db_error(e)

    @classmethod
    async def update(cls: Type[T], filter_: dict[str, Any], **kwargs):
        async with AsyncSessionLocal() as session:
            try:
                query: Update = update(cls).filter_by(**filter_).values(**kwargs).returning(cls)
                result: Result[Any] = await session.execute(query)
                await session.commit()
                return result.scalar_one_or_none()
            except(SQLAlchemyError) as e:
                await session.rollback()
                cls._handle_db_error(e)

    @classmethod
    async def delete(cls: Type[T], filter_: dict[Any, Any]):
        async with AsyncSessionLocal() as session:
            try:
                query: Delete = delete(cls).filter_by(**filter_)
                await session.execute(query)
                await session.commit()
                return True
            except(SQLAlchemyError) as e:
                await session.rollback()
                cls._handle_db_error(e)

    @classmethod
    async def query(cls: Type[T], query):
        async with AsyncSessionLocal() as session:
            try:
                result: Result[Any] = await session.execute(query)
                return result
            except(SQLAlchemyError) as e:
                await session.rollback()
                cls._handle_db_error(e)

    @staticmethod
    async def core_get(query: str, **params):
        async with AsyncSessionLocal() as session:
            try:
                stmt: TextClause = text(query)
                result: Result[Any] = await session.execute(stmt, params)
                return result
            except(SQLAlchemyError) as e:
                await session.rollback()
                Manager._handle_db_error(e)

    @staticmethod
    async def core_commit(query: str, **params):
        async with AsyncSessionLocal() as session:
            try:
                stmt: TextClause = text(query)
                await session.execute(stmt, params)
                await session.commit()
            except (SQLAlchemyError) as e:
                await session.rollback()
                Manager._handle_db_error(e)

    @staticmethod
    def _handle_db_error(e: Exception):
        if isinstance(e, IntegrityError):
            orig_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
            logger.error(f"Ma'lumot nusxalangan/Xatolik: {orig_msg}")
            raise DatabaseException(f"Ma'lumotlar yaxlitligi buzildi: {orig_msg}", original_error=e)

        if isinstance(e, DataError):
            orig_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
            logger.error(f"Noto'g'ri ma'lumot formati: {orig_msg}")
            raise DatabaseException(f"Ma'lumot formatida xato: {orig_msg}", original_error=e)

        logger.error(f"Kutilmagan baza xatosi: {str(e)}", exc_info=True)
        raise DatabaseException(f"Baza xatosi: {str(e)}", original_error=e)


tz: str = "CURRENT_TIMESTAMP"


class Model(Base, Manager):
    __abstract__ = True

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower() + 's'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text(tz))
