import json
import os
import re
from typing import List, Optional

DATA_DIR = "./data/feedback"
MIN_CONFIRMATIONS = 2


class FeedbackGlossary:
    def __init__(self, data_dir: str = DATA_DIR):
        self._data_dir = data_dir
        os.makedirs(self._data_dir, exist_ok=True)

    def _path(self, connection_name: str) -> str:
        return os.path.join(self._data_dir, f"{connection_name}.json")

    def _load(self, connection_name: str) -> dict:
        path = self._path(connection_name)
        if not os.path.exists(path):
            return {"preferences": {}, "corrections": []}
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    def _save(self, connection_name: str, data: dict) -> None:
        with open(self._path(connection_name), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _core_term(self, question: str) -> str:
        lower = re.sub(r"^(show|list|find|get|what|how many|which|give me)\s+", "", question.lower())
        lower = re.sub(r"\b(the|a|an|of|for|in|by|with|all)\b", "", lower)
        return lower.strip()

    def record_preference(
        self,
        connection_name: str,
        question: str,
        chosen_label: str,
        chosen_sql: str,
        all_options: List[dict],
    ) -> None:
        data = self._load(connection_name)
        term = self._core_term(question)
        prefs = data.setdefault("preferences", {})
        if term not in prefs:
            prefs[term] = {"chosen_label": chosen_label, "chosen_sql": chosen_sql, "count": 0, "all_options": all_options}
        prefs[term]["count"] = prefs[term].get("count", 0) + 1
        prefs[term]["chosen_label"] = chosen_label
        prefs[term]["chosen_sql"] = chosen_sql
        self._save(connection_name, data)

    def record_correction(
        self,
        connection_name: str,
        question: str,
        original_sql: str,
        corrected_sql: str,
        explanation: str = "",
    ) -> None:
        data = self._load(connection_name)
        corrections = data.setdefault("corrections", [])
        corrections.append({
            "question": question,
            "original_sql": original_sql,
            "corrected_sql": corrected_sql,
            "explanation": explanation,
        })
        # Keep last 50
        data["corrections"] = corrections[-50:]
        self._save(connection_name, data)

    def get_preference(self, connection_name: str, question: str) -> Optional[dict]:
        data = self._load(connection_name)
        term = self._core_term(question)
        pref = data.get("preferences", {}).get(term)
        if pref and pref.get("count", 0) >= MIN_CONFIRMATIONS:
            return pref
        return None

    def format_for_prompt(self, connection_name: str) -> str:
        data = self._load(connection_name)
        lines = []
        prefs = {k: v for k, v in data.get("preferences", {}).items() if v.get("count", 0) >= MIN_CONFIRMATIONS}
        if prefs:
            lines.append("[Learned user preferences (medium priority)]")
            for term, pref in list(prefs.items())[:10]:
                lines.append(f"- '{term}' → {pref['chosen_label']}: {pref['chosen_sql']}")

        corrections = data.get("corrections", [])[-5:]
        if corrections:
            lines.append("[Recent query corrections]")
            for c in corrections:
                lines.append(f"- Q: {c['question']} | Corrected: {c['corrected_sql']}")
        return "\n".join(lines)


feedback_glossary = FeedbackGlossary()
