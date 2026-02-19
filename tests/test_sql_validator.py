import pytest
from app.validators.sql_validator import SQLValidator


@pytest.fixture
def validator():
    return SQLValidator()


def test_valid_select(validator):
    valid, msg = validator.validate("SELECT * FROM users LIMIT 10")
    assert valid is True
    assert msg == ""


def test_valid_select_with_markdown(validator):
    sql = validator.sanitize("```sql\nSELECT id FROM orders\n```")
    valid, msg = validator.validate(sql)
    assert valid is True


def test_forbidden_drop(validator):
    valid, msg = validator.validate("DROP TABLE users")
    assert valid is False


def test_forbidden_delete(validator):
    valid, msg = validator.validate("DELETE FROM users WHERE id=1")
    assert valid is False


def test_forbidden_update(validator):
    valid, msg = validator.validate("UPDATE users SET name='x'")
    assert valid is False


def test_forbidden_insert(validator):
    valid, msg = validator.validate("INSERT INTO users VALUES (1)")
    assert valid is False


def test_forbidden_truncate(validator):
    valid, msg = validator.validate("TRUNCATE TABLE users")
    assert valid is False


def test_forbidden_alter(validator):
    valid, msg = validator.validate("ALTER TABLE users ADD COLUMN x INT")
    assert valid is False


def test_forbidden_create(validator):
    valid, msg = validator.validate("CREATE TABLE t (id INT)")
    assert valid is False


def test_forbidden_comment_double_dash(validator):
    valid, msg = validator.validate("SELECT * FROM users -- comment")
    assert valid is False


def test_forbidden_comment_block(validator):
    valid, msg = validator.validate("SELECT /* comment */ * FROM users")
    assert valid is False


def test_multiple_statements(validator):
    valid, msg = validator.validate("SELECT 1; DROP TABLE users")
    assert valid is False
    assert "Multiple statements" in msg


def test_empty_sql(validator):
    valid, msg = validator.validate("")
    assert valid is False
    assert "empty" in msg.lower()


def test_not_select(validator):
    valid, msg = validator.validate("SHOW TABLES")
    assert valid is False
    assert "SELECT" in msg


def test_sanitize_removes_semicolon(validator):
    sql = validator.sanitize("SELECT * FROM users;")
    assert not sql.endswith(";")


def test_sanitize_removes_markdown(validator):
    sql = validator.sanitize("```sql\nSELECT 1\n```")
    assert "```" not in sql
    assert sql == "SELECT 1"
