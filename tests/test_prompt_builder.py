import pytest
from app.services.prompt_builder import PromptBuilder


@pytest.fixture
def builder():
    return PromptBuilder()


@pytest.fixture
def sample_schema():
    return {
        "dialect": "postgresql",
        "tables": {
            "customers": {
                "columns": [
                    {"name": "id", "type": "INTEGER", "nullable": False, "primary_key": True},
                    {"name": "name", "type": "VARCHAR", "nullable": False, "primary_key": False},
                    {"name": "email", "type": "VARCHAR", "nullable": True, "primary_key": False},
                ],
                "foreign_keys": [],
                "indexes": [],
                "row_count_estimate": 100,
            },
            "orders": {
                "columns": [
                    {"name": "id", "type": "INTEGER", "nullable": False, "primary_key": True},
                    {"name": "customer_id", "type": "INTEGER", "nullable": False, "primary_key": False},
                    {"name": "total", "type": "NUMERIC", "nullable": True, "primary_key": False},
                ],
                "foreign_keys": [
                    {
                        "columns": ["customer_id"],
                        "referred_table": "customers",
                        "referred_columns": ["id"],
                    }
                ],
                "indexes": [],
                "row_count_estimate": 500,
            },
        },
    }


def test_build_system_prompt_contains_dialect(builder, sample_schema):
    prompt = builder.build_system_prompt(sample_schema)
    assert "postgresql" in prompt.lower() or "POSTGRESQL" in prompt


def test_build_system_prompt_contains_tables(builder, sample_schema):
    prompt = builder.build_system_prompt(sample_schema)
    assert "customers" in prompt
    assert "orders" in prompt


def test_build_system_prompt_contains_columns(builder, sample_schema):
    prompt = builder.build_system_prompt(sample_schema)
    assert "name" in prompt
    assert "email" in prompt
    assert "total" in prompt


def test_build_system_prompt_contains_pk(builder, sample_schema):
    prompt = builder.build_system_prompt(sample_schema)
    assert "PK" in prompt


def test_build_system_prompt_contains_fk(builder, sample_schema):
    prompt = builder.build_system_prompt(sample_schema)
    assert "FK" in prompt or "customer_id" in prompt


def test_build_system_prompt_select_only(builder, sample_schema):
    prompt = builder.build_system_prompt(sample_schema)
    assert "SELECT" in prompt


def test_build_system_prompt_mysql_backtick(builder):
    schema = {
        "dialect": "mysql",
        "tables": {
            "order": {
                "columns": [
                    {"name": "id", "type": "INT", "nullable": False, "primary_key": True},
                ],
                "foreign_keys": [],
            }
        },
    }
    prompt = builder.build_system_prompt(schema)
    assert "`order`" in prompt


def test_build_system_prompt_postgres_double_quote_reserved(builder):
    schema = {
        "dialect": "postgresql",
        "tables": {
            "order": {
                "columns": [
                    {"name": "id", "type": "INT", "nullable": False, "primary_key": True},
                ],
                "foreign_keys": [],
            }
        },
    }
    prompt = builder.build_system_prompt(schema)
    assert '"order"' in prompt


def test_quote_if_reserved(builder):
    assert builder._quote_if_reserved("order", '"') == '"order"'
    assert builder._quote_if_reserved("customers", '"') == "customers"
