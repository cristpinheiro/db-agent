import logging
from typing import Any, Dict, List, Optional

from app.config import settings
from app.services.connection_manager import connection_manager
from app.services.schema_discovery import schema_discovery
from app.services.schema_mapping.mapping_store import mapping_store
from app.services.schema_mapping.sql_translator import SQLTranslator
from app.services.schema_mapping.auto_mapper import AutoMapper
from app.services.glossary.glossary_compositor import glossary_compositor
from app.services.prompt_builder import PromptBuilder
from app.services.query_executor import QueryExecutor
from app.validators.sql_validator import SQLValidator

logger = logging.getLogger(__name__)


class Agent:
    def __init__(self):
        self._prompt_builder = PromptBuilder()
        self._validator = SQLValidator()
        self._executor = QueryExecutor()
        self._auto_mapper = AutoMapper()
        self._llm = None

    def _get_llm(self):
        if self._llm is None:
            from app.services.llm import get_llm_provider
            self._llm = get_llm_provider()
        return self._llm

    def process_question(self, question: str, connection_name: str) -> dict:
        engine = connection_manager.get_engine(connection_name)
        real_schema = schema_discovery.discover(engine, connection_name)
        dialect = real_schema.get("dialect", "unknown")

        mapping = mapping_store.get_mapping(connection_name)
        translator: Optional[SQLTranslator] = None
        if mapping:
            translator = SQLTranslator(mapping)
            schema_for_prompt = self._apply_mapping_to_schema(real_schema, mapping)
        else:
            schema_for_prompt = real_schema

        system_prompt = self._prompt_builder.build_system_prompt(schema_for_prompt)

        try:
            glossary_context = glossary_compositor.build_glossary_prompt(engine, connection_name)
            if glossary_context:
                system_prompt = system_prompt + "\n\n" + glossary_context
        except Exception as e:
            logger.warning("Could not build glossary: %s", e)

        messages = [{"role": "user", "content": question}]
        llm = self._get_llm()

        retry_count = 0
        last_error = None
        sql_display = None
        sql_executed = None

        while retry_count <= settings.max_retries:
            try:
                raw_sql = llm.chat(system_prompt, messages)
                sql_clean = self._validator.sanitize(raw_sql)
                is_valid, error_msg = self._validator.validate(sql_clean)

                if not is_valid:
                    raise ValueError(f"SQL validation failed: {error_msg}")

                sql_display = sql_clean
                if translator:
                    sql_executed = translator.friendly_to_real(sql_clean)
                else:
                    sql_executed = sql_clean

                results, exec_time = self._executor.execute(
                    engine, sql_executed, max_rows=settings.max_result_rows
                )

                return {
                    "question": question,
                    "needs_clarification": False,
                    "ambiguity_detected": False,
                    "ambiguity_type": None,
                    "message": None,
                    "interpretations": [],
                    "perspectives": [
                        {
                            "label": "primary",
                            "interpretation": None,
                            "sql_query": sql_display,
                            "sql_executed": sql_executed,
                            "results": results,
                            "row_count": len(results),
                            "execution_time": exec_time,
                            "success": True,
                            "error": None,
                        }
                    ],
                    "dialect": dialect,
                    "retry_count": retry_count,
                    "success": True,
                    "error_message": None,
                    "mapping_used": translator is not None,
                }

            except Exception as exc:
                last_error = str(exc)
                logger.warning("Attempt %d failed: %s", retry_count + 1, exc)
                messages.append({"role": "assistant", "content": sql_display or ""})
                messages.append({
                    "role": "user",
                    "content": f"The previous SQL failed with error: {last_error}. Please fix it.",
                })
                retry_count += 1

        return {
            "question": question,
            "needs_clarification": False,
            "ambiguity_detected": False,
            "ambiguity_type": None,
            "message": None,
            "interpretations": [],
            "perspectives": [],
            "dialect": dialect,
            "retry_count": retry_count,
            "success": False,
            "error_message": last_error,
            "mapping_used": translator is not None,
        }

    def _apply_mapping_to_schema(self, real_schema: dict, mapping: dict) -> dict:
        tables_mapping = mapping.get("tables", {})
        virtual_tables = {}

        for real_table, tdata in real_schema.get("tables", {}).items():
            tmap = tables_mapping.get(real_table, {})
            friendly_table = tmap.get("friendly_name", real_table)
            col_map = tmap.get("columns", {})

            virtual_columns = []
            for col in tdata.get("columns", []):
                if isinstance(col, dict):
                    real_col = col["name"]
                    cmap = col_map.get(real_col, {})
                    friendly_col = cmap.get("friendly_name", real_col)
                    virtual_columns.append({**col, "name": friendly_col})
                else:
                    virtual_columns.append(col)

            virtual_fks = []
            for fk in tdata.get("foreign_keys", []):
                ref_real = fk.get("referred_table", "")
                ref_map = tables_mapping.get(ref_real, {})
                ref_friendly = ref_map.get("friendly_name", ref_real)
                virtual_fks.append({**fk, "referred_table": ref_friendly})

            virtual_tables[friendly_table] = {
                **tdata,
                "columns": virtual_columns,
                "foreign_keys": virtual_fks,
            }

        return {**real_schema, "tables": virtual_tables}


agent = Agent()
