import pytest
from sqlalchemy import create_engine, text


@pytest.fixture
def sqlite_engine():
    engine = create_engine("sqlite:///:memory:")
    with engine.connect() as conn:
        conn.execute(text(
            "CREATE TABLE customers (id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT)"
        ))
        conn.execute(text(
            "CREATE TABLE orders (id INTEGER PRIMARY KEY, customer_id INTEGER, total REAL, "
            "FOREIGN KEY (customer_id) REFERENCES customers(id))"
        ))
        conn.execute(text("INSERT INTO customers VALUES (1, 'Alice', 'alice@example.com')"))
        conn.execute(text("INSERT INTO orders VALUES (1, 1, 99.99)"))
        conn.commit()
    return engine
