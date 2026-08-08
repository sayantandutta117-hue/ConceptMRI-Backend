import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy import Uuid

# Check what CREATE TABLE looks like for both types on SQLite
from sqlalchemy.schema import CreateTable
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class Test1(Base):
    __tablename__ = "test1"
    id: Mapped[int] = mapped_column(PGUUID(as_uuid=True), primary_key=True)

class Test2(Base):
    __tablename__ = "test2"
    id: Mapped[int] = mapped_column(Uuid(as_uuid=True), primary_key=True)

engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=True, future=True)

import asyncio

async def main():
    async with engine.begin() as conn:
        # Just print the compiled SQL
        from sqlalchemy.dialects.sqlite import dialect as sqlite_dialect
        print("PGUUID CreateTable:")
        print(CreateTable(Test1.__table__).compile(dialect=sqlite_dialect()))
        print("\nUuid CreateTable:")
        print(CreateTable(Test2.__table__).compile(dialect=sqlite_dialect()))

asyncio.run(main())
