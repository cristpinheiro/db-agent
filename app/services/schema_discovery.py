from typing import Dict
from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy import inspect as sa_inspect
from sqlalchemy.sql.elements import quoted_name


class SchemaDiscovery:
    def __init__(self):
        self._cache: Dict[str, Dict] = {}

    def discover(self, engine: Engine, connection_name: str, force: bool = False) -> dict:
        if not force and connection_name in self._cache:
            return self._cache[connection_name]

        inspector = sa_inspect(engine)
        dialect = engine.dialect.name
        tables = {}

        for table_name in inspector.get_table_names():
            columns = []
            pk_columns = inspector.get_pk_constraint(table_name).get("constrained_columns", [])
            for col in inspector.get_columns(table_name):
                columns.append({
                    "name": col["name"],
                    "type": str(col["type"]),
                    "nullable": col.get("nullable", True),
                    "primary_key": col["name"] in pk_columns,
                })

            fks = []
            for fk in inspector.get_foreign_keys(table_name):
                fks.append({
                    "columns": fk.get("constrained_columns", []),
                    "referred_table": fk.get("referred_table", ""),
                    "referred_columns": fk.get("referred_columns", []),
                })

            indexes = []
            for idx in inspector.get_indexes(table_name):
                indexes.append({
                    "name": idx.get("name"),
                    "columns": idx.get("column_names", []),
                    "unique": idx.get("unique", False),
                })

            row_count_estimate = self._estimate_row_count(engine, dialect, table_name)

            tables[table_name] = {
                "columns": columns,
                "foreign_keys": fks,
                "indexes": indexes,
                "row_count_estimate": row_count_estimate,
            }

        result = {"dialect": dialect, "tables": tables}
        self._cache[connection_name] = result
        return result

    def _estimate_row_count(self, engine: Engine, dialect: str, table_name: str) -> int:
        try:
            if dialect == "postgresql":
                with engine.connect() as conn:
                    row = conn.execute(
                        text(
                            "SELECT reltuples::bigint FROM pg_class WHERE relname = :t"
                        ),
                        {"t": table_name},
                    ).fetchone()
                    if row:
                        return int(row[0])
            with engine.connect() as conn:
                safe_table = quoted_name(table_name, quote=True)
                row = conn.execute(
                    text(f"SELECT COUNT(*) FROM {safe_table}")
                ).fetchone()
                if row:
                    return int(row[0])
        except Exception:
            pass
        return 0

    def invalidate(self, connection_name: str) -> None:
        self._cache.pop(connection_name, None)


schema_discovery = SchemaDiscovery()
