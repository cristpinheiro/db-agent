import re
from typing import Tuple


FORBIDDEN_PATTERNS = [
    r"\bDROP\b",
    r"\bDELETE\b",
    r"\bUPDATE\b",
    r"\bINSERT\b",
    r"\bTRUNCATE\b",
    r"\bALTER\b",
    r"\bCREATE\b",
    r"\bGRANT\b",
    r"\bREVOKE\b",
    r"\bEXEC\b",
    r"\bEXECUTE\b",
    r"\bCALL\b",
    r"INTO\s+OUTFILE",
    r"LOAD\s+DATA",
    r"\bpg_catalog\b",
    r"\binformation_schema\b",
    r"--",
    r"/\*",
]


class SQLValidator:
    def validate(self, sql: str) -> Tuple[bool, str]:
        if not sql or not sql.strip():
            return False, "SQL is empty"

        clean = self.sanitize(sql)

        if ";" in clean:
            return False, "Multiple statements are not allowed"

        if not clean.upper().startswith("SELECT"):
            return False, "Only SELECT statements are allowed"

        upper = clean.upper()
        for pattern in FORBIDDEN_PATTERNS:
            if re.search(pattern, upper, re.IGNORECASE):
                return False, f"Forbidden pattern detected: {pattern}"

        return True, ""

    def _clean_sql(self, sql: str) -> str:
        sql = re.sub(r"```sql\s*", "", sql, flags=re.IGNORECASE)
        sql = re.sub(r"```\s*", "", sql)
        return sql.strip()

    def sanitize(self, sql: str) -> str:
        sql = self._clean_sql(sql)
        sql = sql.rstrip(";").strip()
        return sql
