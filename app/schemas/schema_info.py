from typing import List, Optional
from pydantic import BaseModel


class ColumnInfo(BaseModel):
    name: str
    type: str
    nullable: bool
    primary_key: bool


class ForeignKeyInfo(BaseModel):
    columns: List[str]
    referred_table: str
    referred_columns: List[str]


class TableInfo(BaseModel):
    name: str
    columns: List[ColumnInfo]
    foreign_keys: List[ForeignKeyInfo]
    row_count_estimate: Optional[int] = None


class SchemaResponse(BaseModel):
    connection_name: str
    dialect: str
    tables: List[TableInfo]
