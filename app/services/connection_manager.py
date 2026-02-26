from typing import Dict, List
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine


class ConnectionManager:
    def __init__(self):
        self._engines: Dict[str, Engine] = {}

    def register(self, name: str, url: str) -> dict:
        engine = create_engine(
            url,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
        )
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        self._engines[name] = engine
        dialect = engine.dialect.name
        from app.services.schema_discovery import schema_discovery
        schema_info = schema_discovery.discover(engine, name)
        tables_count = len(schema_info.get("tables", {}))
        return {
            "name": name,
            "dialect": dialect,
            "connected": True,
            "tables_count": tables_count,
        }

    def get_engine(self, name: str) -> Engine:
        if name not in self._engines:
            raise KeyError(f"Connection '{name}' not found")
        return self._engines[name]

    def remove(self, name: str) -> None:
        if name in self._engines:
            self._engines[name].dispose()
            del self._engines[name]

    def list_connections(self) -> List[dict]:
        result = []
        from app.services.schema_discovery import schema_discovery
        for name, engine in self._engines.items():
            try:
                schema_info = schema_discovery.discover(engine, name)
                tables_count = len(schema_info.get("tables", {}))
                connected = True
            except Exception:
                tables_count = 0
                connected = False
            result.append({
                "name": name,
                "dialect": engine.dialect.name,
                "connected": connected,
                "tables_count": tables_count,
            })
        return result


connection_manager = ConnectionManager()
