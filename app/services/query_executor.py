import time
from typing import Any, Dict, List, Tuple

from sqlalchemy import text
from sqlalchemy.engine import Engine


class QueryExecutor:
    def execute(
        self, engine: Engine, sql: str, max_rows: int = 500
    ) -> Tuple[List[Dict[str, Any]], float]:
        start = time.time()
        with engine.connect() as conn:
            result = conn.execute(text(sql))
            rows = result.fetchmany(max_rows)
            columns = list(result.keys())
            records = [dict(zip(columns, row)) for row in rows]
        elapsed = time.time() - start
        return records, elapsed
