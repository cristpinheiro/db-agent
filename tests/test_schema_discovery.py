import pytest
from app.services.schema_discovery import SchemaDiscovery


def test_schema_discovery_basic(sqlite_engine):
    discovery = SchemaDiscovery()
    result = discovery.discover(sqlite_engine, "test_conn")
    assert result["dialect"] == "sqlite"
    assert "customers" in result["tables"]
    assert "orders" in result["tables"]


def test_schema_discovery_columns(sqlite_engine):
    discovery = SchemaDiscovery()
    result = discovery.discover(sqlite_engine, "test_conn2")
    customers = result["tables"]["customers"]
    col_names = [c["name"] for c in customers["columns"]]
    assert "id" in col_names
    assert "name" in col_names
    assert "email" in col_names


def test_schema_discovery_pk(sqlite_engine):
    discovery = SchemaDiscovery()
    result = discovery.discover(sqlite_engine, "test_conn3")
    customers = result["tables"]["customers"]
    pk_cols = [c["name"] for c in customers["columns"] if c["primary_key"]]
    assert "id" in pk_cols


def test_schema_discovery_foreign_keys(sqlite_engine):
    discovery = SchemaDiscovery()
    result = discovery.discover(sqlite_engine, "test_conn4")
    orders = result["tables"]["orders"]
    assert len(orders["foreign_keys"]) > 0
    fk = orders["foreign_keys"][0]
    assert fk["referred_table"] == "customers"


def test_schema_discovery_cache(sqlite_engine):
    discovery = SchemaDiscovery()
    result1 = discovery.discover(sqlite_engine, "cached_conn")
    result2 = discovery.discover(sqlite_engine, "cached_conn")
    assert result1 is result2


def test_schema_discovery_invalidate(sqlite_engine):
    discovery = SchemaDiscovery()
    result1 = discovery.discover(sqlite_engine, "inv_conn")
    discovery.invalidate("inv_conn")
    result2 = discovery.discover(sqlite_engine, "inv_conn")
    assert result1 is not result2
