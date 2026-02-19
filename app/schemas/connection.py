from typing import List
from pydantic import BaseModel


class ConnectionCreate(BaseModel):
    name: str
    url: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"name": "postgres_db", "url": "postgresql://user:pass@localhost:5432/mydb"},
                {"name": "mysql_db", "url": "mysql+pymysql://user:pass@localhost:3306/mydb"},
                {"name": "sqlite_db", "url": "sqlite:///./mydb.sqlite"},
            ]
        }
    }


class ConnectionResponse(BaseModel):
    name: str
    dialect: str
    connected: bool
    tables_count: int


class ConnectionListResponse(BaseModel):
    connections: List[ConnectionResponse]
