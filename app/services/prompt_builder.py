RESERVED_WORDS = {
    "order", "group", "user", "table", "select", "index",
    "key", "check", "default",
}


class PromptBuilder:
    def build_system_prompt(self, schema_info: dict) -> str:
        dialect = schema_info.get("dialect", "unknown")
        tables = schema_info.get("tables", {})

        if dialect == "postgresql":
            quote = '"'
        elif dialect == "mysql":
            quote = "`"
        else:
            quote = '"'

        lines = [
            f"You are a {dialect.upper()} SQL expert.",
            f"Database dialect: {dialect}",
            "Generate ONLY valid SQL. No markdown, no comments, no explanations.",
            "",
            "SAFETY RULES:",
            "- Only SELECT statements are allowed.",
            "- No DDL (CREATE, ALTER, DROP) or DML (INSERT, UPDATE, DELETE).",
            "- Always use explicit JOINs.",
            "- Add ORDER BY when appropriate.",
            "- Add LIMIT 100 by default unless otherwise specified.",
            "",
        ]

        if dialect == "postgresql":
            lines += [
                'QUOTING: Use double quotes for identifiers with uppercase or reserved words.',
                'Example: SELECT "Name" FROM "Order" LIMIT 100;',
                "",
            ]
        elif dialect == "mysql":
            lines += [
                "QUOTING: Use backticks for identifiers with reserved words.",
                "Example: SELECT `name` FROM `order` LIMIT 100;",
                "",
            ]

        lines.append("SCHEMA:")
        for table_name, tdata in tables.items():
            quoted_table = self._quote_if_reserved(table_name, quote)
            pk_cols = [
                c["name"] if isinstance(c, dict) else c
                for c in tdata.get("columns", [])
                if isinstance(c, dict) and c.get("primary_key")
            ]
            pk_str = f" [PK: {', '.join(pk_cols)}]" if pk_cols else ""
            lines.append(f"\nTable: {quoted_table}{pk_str}")
            for col in tdata.get("columns", []):
                if isinstance(col, dict):
                    col_name = self._quote_if_reserved(col["name"], quote)
                    col_type = col.get("type", "")
                    nullable = "" if col.get("nullable", True) else " NOT NULL"
                    pk_mark = " (PK)" if col.get("primary_key") else ""
                    lines.append(f"  - {col_name}: {col_type}{nullable}{pk_mark}")
                else:
                    lines.append(f"  - {self._quote_if_reserved(col, quote)}")

            for fk in tdata.get("foreign_keys", []):
                fk_cols = ", ".join(fk.get("columns", []))
                ref_table = fk.get("referred_table", "")
                ref_cols = ", ".join(fk.get("referred_columns", []))
                lines.append(f"  FK: ({fk_cols}) -> {ref_table}({ref_cols})")

        return "\n".join(lines)

    def _quote_if_reserved(self, name: str, quote: str) -> str:
        if name.lower() in RESERVED_WORDS:
            return f"{quote}{name}{quote}"
        return name
