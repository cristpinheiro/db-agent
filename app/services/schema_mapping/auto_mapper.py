import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)

ERP_TABLE_HINTS = {
    "SA1": "customers",
    "SA2": "suppliers",
    "SB1": "products",
    "SC5": "sales_orders",
    "SC6": "sales_order_items",
    "SE1": "accounts_receivable",
    "SE2": "accounts_payable",
    "SF2": "invoices",
    "SD1": "delivery_items",
    "SD2": "deliveries",
}

COL_PATTERNS = {
    "nome": "name",
    "cod": "code",
    "cgc": "tax_id",
    "cpf": "cpf",
    "valor": "value",
    "qtd": "quantity",
    "emissao": "issue_date",
    "vencto": "due_date",
    "loja": "store",
    "tipo": "type",
    "status": "status",
    "obs": "notes",
    "end": "address",
    "cid": "city",
    "est": "state",
    "pais": "country",
    "tel": "phone",
    "email": "email",
    "preco": "price",
    "desc": "discount",
    "saldo": "balance",
    "data": "date",
}


class AutoMapper:
    def __init__(self):
        self._llm = None

    def _get_llm(self):
        if self._llm is None:
            from app.services.llm import get_llm_provider
            self._llm = get_llm_provider()
        return self._llm

    def generate_mapping(self, schema_info: dict, erp_hint: str = "") -> dict:
        mapping = {"tables": {}}
        tables = schema_info.get("tables", {})

        # Try LLM first
        try:
            llm_mapping = self._llm_mapping(schema_info, erp_hint)
            if llm_mapping:
                return llm_mapping
        except Exception as e:
            logger.warning("LLM auto-mapping failed, falling back to heuristics: %s", e)

        # Heuristic fallback
        for real_table, tdata in tables.items():
            friendly_table = self._infer_table_name(real_table)
            cols_mapping = {}
            for col in tdata.get("columns", []):
                col_name = col["name"] if isinstance(col, dict) else col
                col_type = col.get("type", "") if isinstance(col, dict) else ""
                friendly_col = self._infer_col_name(col_name)
                btype = self._infer_business_type(col_name, col_type)
                cols_mapping[col_name] = {
                    "friendly_name": friendly_col,
                    "description": "",
                    "business_type": btype,
                }
            mapping["tables"][real_table] = {
                "friendly_name": friendly_table,
                "description": "",
                "columns": cols_mapping,
            }
        return mapping

    def _llm_mapping(self, schema_info: dict, erp_hint: str) -> Optional[dict]:
        llm = self._get_llm()
        tables_summary = []
        for tname, tdata in list(schema_info.get("tables", {}).items())[:20]:
            col_names = [c["name"] if isinstance(c, dict) else c for c in tdata.get("columns", [])]
            tables_summary.append(f"- {tname}: {', '.join(col_names[:10])}")
        tables_text = "\n".join(tables_summary)
        hint_text = f"\nERP hint: {erp_hint}" if erp_hint else ""
        system_prompt = (
            "You are a database expert. Given a list of tables and columns with cryptic names "
            "(like ERP systems), produce a JSON mapping with friendly names.\n"
            "Return ONLY valid JSON in this format:\n"
            '{"tables": {"REAL_TABLE": {"friendly_name": "...", "description": "...", '
            '"columns": {"REAL_COL": {"friendly_name": "...", "description": "...", "business_type": "..."}}}}}'
        )
        user_msg = f"Map these tables/columns to friendly names:{hint_text}\n\n{tables_text}"
        response = llm.chat(system_prompt, [{"role": "user", "content": user_msg}])
        # Extract JSON from response
        start = response.find("{")
        end = response.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(response[start:end])
        return None

    def _infer_table_name(self, name: str) -> str:
        upper = name.upper()
        for prefix, friendly in ERP_TABLE_HINTS.items():
            if upper.startswith(prefix):
                return friendly
        return name.lower()

    def _infer_col_name(self, name: str) -> str:
        lower = name.lower()
        for pattern, friendly in COL_PATTERNS.items():
            if pattern in lower:
                return friendly
        return name.lower()

    def _infer_business_type(self, name: str, col_type: str) -> str:
        lower_name = name.lower()
        lower_type = col_type.lower()
        if any(x in lower_name for x in ["cod", "id", "key", "num"]):
            return "identifier"
        if any(x in lower_name for x in ["valor", "preco", "price", "value", "amount"]):
            return "currency"
        if any(x in lower_type for x in ["numeric", "decimal", "float", "int"]):
            return "numeric"
        if any(x in lower_name for x in ["data", "date", "emissao", "vencto"]):
            return "date"
        if any(x in lower_name for x in ["flag", "ativo", "active", "status"]):
            return "flag"
        return "text"
