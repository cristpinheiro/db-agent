import json
import os

DATA_DIR = "./data/glossary"


class AdminGlossary:
    def __init__(self, data_dir: str = DATA_DIR):
        self._data_dir = data_dir
        os.makedirs(self._data_dir, exist_ok=True)

    def _path(self, connection_name: str) -> str:
        return os.path.join(self._data_dir, f"{connection_name}.json")

    def _load(self, connection_name: str) -> dict:
        path = self._path(connection_name)
        if not os.path.exists(path):
            return {"terms": {}}
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    def _save(self, connection_name: str, data: dict) -> None:
        with open(self._path(connection_name), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def add_term(
        self,
        connection_name: str,
        term: str,
        definition: str,
        sql_pattern: str = "",
        notes: str = "",
    ) -> None:
        data = self._load(connection_name)
        data["terms"][term] = {
            "definition": definition,
            "sql_pattern": sql_pattern,
            "notes": notes,
        }
        self._save(connection_name, data)

    def remove_term(self, connection_name: str, term: str) -> bool:
        data = self._load(connection_name)
        if term in data["terms"]:
            del data["terms"][term]
            self._save(connection_name, data)
            return True
        return False

    def get_terms(self, connection_name: str) -> dict:
        return self._load(connection_name).get("terms", {})

    def format_for_prompt(self, connection_name: str) -> str:
        terms = self.get_terms(connection_name)
        if not terms:
            return ""
        lines = ["[Admin-defined terms (highest priority)]"]
        for term, tdata in terms.items():
            line = f"- {term}: {tdata['definition']}"
            if tdata.get("sql_pattern"):
                line += f" | SQL: {tdata['sql_pattern']}"
            lines.append(line)
        return "\n".join(lines)


admin_glossary = AdminGlossary()
