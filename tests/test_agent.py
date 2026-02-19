import pytest
from unittest.mock import MagicMock, patch
from app.services.agent import Agent
from app.validators.sql_validator import SQLValidator


@pytest.fixture
def mock_agent():
    agent = Agent()
    agent._llm = MagicMock()
    return agent


def test_agent_process_question_success(mock_agent, sqlite_engine):
    mock_agent._llm.chat.return_value = "SELECT * FROM customers LIMIT 10"

    with patch("app.services.agent.connection_manager") as mock_cm, \
         patch("app.services.agent.schema_discovery") as mock_sd, \
         patch("app.services.agent.mapping_store") as mock_ms, \
         patch("app.services.agent.glossary_compositor") as mock_gc:

        mock_cm.get_engine.return_value = sqlite_engine
        mock_sd.discover.return_value = {
            "dialect": "sqlite",
            "tables": {
                "customers": {
                    "columns": [
                        {"name": "id", "type": "INTEGER", "nullable": False, "primary_key": True},
                        {"name": "name", "type": "TEXT", "nullable": False, "primary_key": False},
                    ],
                    "foreign_keys": [],
                }
            },
        }
        mock_ms.get_mapping.return_value = None
        mock_gc.build_glossary_prompt.return_value = ""

        result = mock_agent.process_question("Show all customers", "test")

    assert result["success"] is True
    assert len(result["perspectives"]) == 1
    assert result["perspectives"][0]["row_count"] >= 0


def test_agent_process_question_invalid_sql(mock_agent, sqlite_engine):
    mock_agent._llm.chat.return_value = "DROP TABLE customers"

    with patch("app.services.agent.connection_manager") as mock_cm, \
         patch("app.services.agent.schema_discovery") as mock_sd, \
         patch("app.services.agent.mapping_store") as mock_ms, \
         patch("app.services.agent.glossary_compositor") as mock_gc:

        mock_cm.get_engine.return_value = sqlite_engine
        mock_sd.discover.return_value = {
            "dialect": "sqlite",
            "tables": {},
        }
        mock_ms.get_mapping.return_value = None
        mock_gc.build_glossary_prompt.return_value = ""

        result = mock_agent.process_question("Drop customers table", "test")

    assert result["success"] is False


def test_agent_apply_mapping_to_schema():
    agent = Agent()
    real_schema = {
        "dialect": "sqlite",
        "tables": {
            "SA1010": {
                "columns": [
                    {"name": "A1_COD", "type": "VARCHAR", "nullable": False, "primary_key": True},
                    {"name": "A1_NOME", "type": "VARCHAR", "nullable": True, "primary_key": False},
                ],
                "foreign_keys": [],
            }
        },
    }
    mapping = {
        "tables": {
            "SA1010": {
                "friendly_name": "customers",
                "description": "Customer table",
                "columns": {
                    "A1_COD": {"friendly_name": "customer_code", "description": "", "business_type": "identifier"},
                    "A1_NOME": {"friendly_name": "customer_name", "description": "", "business_type": "text"},
                },
            }
        }
    }
    virtual = agent._apply_mapping_to_schema(real_schema, mapping)
    assert "customers" in virtual["tables"]
    col_names = [c["name"] for c in virtual["tables"]["customers"]["columns"]]
    assert "customer_code" in col_names
    assert "customer_name" in col_names
