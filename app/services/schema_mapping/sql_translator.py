import re
from typing import Dict


class SQLTranslator:
    def __init__(self, mapping: dict):
        self._mapping = mapping
        self._table_to_real: Dict[str, str] = {}
        self._table_to_friendly: Dict[str, str] = {}
        self._col_to_real: Dict[str, Dict[str, str]] = {}
        self._col_to_friendly: Dict[str, Dict[str, str]] = {}
        self._build_maps()

    def _build_maps(self):
        tables = self._mapping.get("tables", {})
        for real_table, tdata in tables.items():
            friendly_table = tdata.get("friendly_name", real_table)
            self._table_to_real[friendly_table] = real_table
            self._table_to_friendly[real_table] = friendly_table
            real_cols: Dict[str, str] = {}
            friendly_cols: Dict[str, str] = {}
            for real_col, cdata in tdata.get("columns", {}).items():
                friendly_col = cdata.get("friendly_name", real_col)
                real_cols[friendly_col] = real_col
                friendly_cols[real_col] = friendly_col
            self._col_to_real[friendly_table] = real_cols
            self._col_to_friendly[real_table] = friendly_cols

    def friendly_to_real(self, sql: str) -> str:
        # Replace table names (longest first)
        for friendly, real in sorted(
            self._table_to_real.items(), key=lambda x: -len(x[0])
        ):
            sql = re.sub(rf"\b{re.escape(friendly)}\b", real, sql)
        # Replace column names
        for friendly_table, cols in self._col_to_real.items():
            real_table = self._table_to_real.get(friendly_table, friendly_table)
            for friendly_col, real_col in sorted(
                cols.items(), key=lambda x: -len(x[0])
            ):
                sql = re.sub(rf"\b{re.escape(friendly_col)}\b", real_col, sql)
        return sql

    def real_to_friendly(self, sql: str) -> str:
        # Replace table names (longest first)
        for real, friendly in sorted(
            self._table_to_friendly.items(), key=lambda x: -len(x[0])
        ):
            sql = re.sub(rf"\b{re.escape(real)}\b", friendly, sql)
        # Replace column names
        for real_table, cols in self._col_to_friendly.items():
            for real_col, friendly_col in sorted(
                cols.items(), key=lambda x: -len(x[0])
            ):
                sql = re.sub(rf"\b{re.escape(real_col)}\b", friendly_col, sql)
        return sql
