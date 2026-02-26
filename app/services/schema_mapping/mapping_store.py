import json
import os
from typing import Optional


DATA_DIR = "./data/mappings"


class MappingStore:
    def __init__(self, data_dir: str = DATA_DIR):
        self._data_dir = data_dir
        os.makedirs(self._data_dir, exist_ok=True)

    def _path(self, connection_name: str) -> str:
        return os.path.join(self._data_dir, f"{connection_name}.json")

    def set_mapping(self, connection_name: str, mapping: dict) -> None:
        with open(self._path(connection_name), "w", encoding="utf-8") as f:
            json.dump(mapping, f, indent=2, ensure_ascii=False)

    def get_mapping(self, connection_name: str) -> Optional[dict]:
        path = self._path(connection_name)
        if not os.path.exists(path):
            return None
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    def update_table(
        self,
        connection_name: str,
        real_table: str,
        friendly_name: str,
        description: str = "",
    ) -> None:
        mapping = self.get_mapping(connection_name) or {"tables": {}}
        if real_table not in mapping["tables"]:
            mapping["tables"][real_table] = {"columns": {}}
        mapping["tables"][real_table]["friendly_name"] = friendly_name
        mapping["tables"][real_table]["description"] = description
        self.set_mapping(connection_name, mapping)

    def update_column(
        self,
        connection_name: str,
        real_table: str,
        real_column: str,
        friendly_name: str,
        description: str = "",
        business_type: str = "",
    ) -> None:
        mapping = self.get_mapping(connection_name) or {"tables": {}}
        if real_table not in mapping["tables"]:
            mapping["tables"][real_table] = {"columns": {}}
        columns = mapping["tables"][real_table].setdefault("columns", {})
        columns[real_column] = {
            "friendly_name": friendly_name,
            "description": description,
            "business_type": business_type,
        }
        self.set_mapping(connection_name, mapping)


mapping_store = MappingStore()
