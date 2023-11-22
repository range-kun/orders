from fastapi import HTTPException
from starlette import status


class NoRowsFoundError(HTTPException):
    def __init__(self, table, filters):
        message = f"No rows found for table {table} with next filters: {filters}"
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=message)


class DbError(Exception):
    pass


class AlreadyExistError(Exception):
    pass


class UpdateError(Exception):
    pass


class MultipleRowsFoundError(Exception):
    pass


class CategoryNotExistsError(HTTPException):
    def __init__(self, id_, status_code=status.HTTP_404_NOT_FOUND):
        message = f"Category with id {id_} not exists"
        super().__init__(status_code=status_code, detail=message)


class NoDataError(Exception):
    pass
