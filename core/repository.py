from sqlalchemy import Table
from sqlalchemy.exc import IntegrityError, MultipleResultsFound, NoResultFound
from sqlalchemy.ext.asyncio import AsyncConnection

from core.errors import (
    AlreadyExistError,
    DbError,
    MultipleRowsFoundError,
    NoRowsFoundError,
    UpdateError,
)


class BaseAlchemyRepository:
    table: Table

    def __init__(self, connection: AsyncConnection):
        self.connection = connection

    async def create(self, data: dict):
        stmt = self.table.insert().values(**data).returning(self.table)
        try:
            row = await self.connection.execute(stmt)
            instance = row.one()
        except IntegrityError:
            raise AlreadyExistError(f"object {self.table} already exist or no related tables with it")
        return dict(instance._mapping)

    async def update(self, data: dict, **filters):
        if not data:
            raise DbError(f"Passed empty dictionary for update method in model {self.table}")

        stmt = self.table.update()
        if filters:
            for field, value in filters.items():
                stmt = stmt.where(self.table.c[field] == value)
        stmt = stmt.values(**data).returning(self.table)

        try:
            rows = await self.connection.execute(stmt)
        except IntegrityError:
            raise UpdateError(f"Db error while updating object from table {self.table}")
        if not rows.rowcount:
            raise NoRowsFoundError(table=self.table, filters=filters)
        return [dict(row._mapping) for row in rows.all()]

    async def delete(self, **filters):
        result = await self.connection.execute(self.table.delete().filter_by(**filters))
        if not result.rowcount:
            raise NoRowsFoundError(table=self.table, filters=filters)
        await self.connection.commit()

    async def get_single(self, **filters):
        row = await self.connection.execute(self.table.select().filter_by(**filters))
        try:
            result = row.one()
        except NoResultFound:
            raise NoRowsFoundError(table=self.table, filters=filters)
        except MultipleResultsFound:
            raise MultipleRowsFoundError(f"Multiple rows found for table {self.table} with next filters: {filters}")
        return dict(result._mapping)
