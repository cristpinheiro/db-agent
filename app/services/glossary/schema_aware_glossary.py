from typing import Dict, List


METRIC_PATTERNS = {
    "quantity": "SUM",
    "qty": "SUM",
    "amount": "SUM",
    "price": "SUM",
    "value": "SUM",
    "total": "SUM",
    "revenue": "SUM",
    "date": "MAX",
    "timestamp": "MAX",
    "rating": "AVG",
    "score": "AVG",
    "count": "COUNT",
}

ENTITY_PATTERNS = {
    "customer": ["customer", "client", "buyer"],
    "seller": ["seller", "employee", "vendor", "salesperson"],
    "product": ["product", "item", "article", "sku"],
    "order": ["order", "sale", "transaction", "purchase"],
    "employee": ["employee", "staff", "worker"],
}


class SchemaAwareGlossary:
    def __init__(self):
        self._cache: Dict[str, dict] = {}

    def build(self, schema_info: dict, connection_name: str) -> dict:
        if connection_name in self._cache:
            return self._cache[connection_name]

        terms: Dict[str, str] = {}
        tables = schema_info.get("tables", {})

        for table_name, tdata in tables.items():
            entity = self._detect_entity(table_name)
            for col in tdata.get("columns", []):
                col_name = col["name"] if isinstance(col, dict) else col
                agg = self._detect_metric(col_name)
                if agg and entity:
                    term = f"{entity}_{col_name}"
                    terms[term] = f"{agg}({table_name}.{col_name})"

        # Common business terms
        for table_name, tdata in tables.items():
            col_names = [
                (c["name"] if isinstance(c, dict) else c) for c in tdata.get("columns", [])
            ]
            if any("qty" in c.lower() or "quantity" in c.lower() for c in col_names):
                terms["most sold"] = "ORDER BY SUM(quantity) DESC"
            if any("price" in c.lower() or "value" in c.lower() for c in col_names):
                terms["revenue"] = "SUM(price * quantity)"

        result = {"terms": terms}
        self._cache[connection_name] = result
        return result

    def _detect_metric(self, col_name: str) -> str:
        lower = col_name.lower()
        for pattern, agg in METRIC_PATTERNS.items():
            if pattern in lower:
                return agg
        return ""

    def _detect_entity(self, table_name: str) -> str:
        lower = table_name.lower()
        for entity, patterns in ENTITY_PATTERNS.items():
            if any(p in lower for p in patterns):
                return entity
        return ""

    def format_for_prompt(self, schema_info: dict, connection_name: str) -> str:
        glossary = self.build(schema_info, connection_name)
        terms = glossary.get("terms", {})
        if not terms:
            return ""
        lines = ["[Schema-inferred terms (lowest priority)]"]
        for term, definition in terms.items():
            lines.append(f"- {term}: {definition}")
        return "\n".join(lines)

    def invalidate(self, connection_name: str) -> None:
        self._cache.pop(connection_name, None)


schema_aware_glossary = SchemaAwareGlossary()
