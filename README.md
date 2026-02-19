# DB Agent - Database Agnostic AI Agent

A production-ready AI agent that connects to any database, discovers its schema automatically, and answers natural language questions by generating, validating, and executing SQL queries.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        FastAPI App                          │
│  /connections  /schema  /query  /mappings  /glossary        │
└───────────────────────┬─────────────────────────────────────┘
                        │
              ┌─────────▼──────────┐
              │   Agent (Orchestr) │
              └──┬──────┬──────────┘
                 │      │
    ┌────────────▼┐  ┌──▼────────────┐
    │  LLM Layer  │  │ Schema Layer  │
    │  (Ollama /  │  │  Discovery +  │
    │   OpenAI)   │  │   Mapping     │
    └─────────────┘  └───────────────┘
                 │
    ┌────────────▼────────────┐
    │  SQL Validator +        │
    │  Query Executor         │
    └─────────────────────────┘
```

## Features

- **Database-agnostic**: PostgreSQL, MySQL, SQLite, and any SQLAlchemy-supported DB
- **Schema auto-discovery**: Introspects tables, columns, PKs, FKs, and indexes at runtime
- **Pluggable LLM**: Supports Ollama (local) and OpenAI
- **ERP-ready**: Schema mapping layer for cryptic naming conventions (SA1, A1_COD, etc.)
- **Business glossary**: 3-layer system (Admin > Feedback > Schema-inferred)
- **SQL validation**: Security-first, SELECT-only enforcement
- **Retry logic**: Automatically retries with error context on failure

## Quick Start

```bash
# Copy and configure environment
cp .env.example .env

# Start with Docker Compose
docker compose up -d
```

## API Usage

### Register a connection
```bash
curl -X POST http://localhost:8000/connections/ \
  -H "Content-Type: application/json" \
  -d '{"name": "mydb", "url": "sqlite:///./mydb.sqlite"}'
```

### Discover schema
```bash
curl http://localhost:8000/schema/mydb
```

### Ask a question
```bash
curl -X POST http://localhost:8000/query/ \
  -H "Content-Type: application/json" \
  -d '{"question": "How many customers do we have?", "connection_name": "mydb"}'
```

### Auto-map ERP schema
```bash
curl -X POST http://localhost:8000/mappings/mydb/auto \
  -H "Content-Type: application/json" \
  -d '{"erp_hint": "TOTVS Protheus"}'
```

### Add admin glossary term
```bash
curl -X POST http://localhost:8000/glossary/mydb/terms \
  -H "Content-Type: application/json" \
  -d '{"term": "revenue", "definition": "Total sales value", "sql_pattern": "SUM(total)"}'
```

### Submit query correction
```bash
curl -X POST http://localhost:8000/glossary/mydb/correction \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Show top customers",
    "original_sql": "SELECT * FROM customers LIMIT 10",
    "corrected_sql": "SELECT name, SUM(total) as revenue FROM customers JOIN orders ON customers.id = orders.customer_id GROUP BY name ORDER BY revenue DESC LIMIT 10",
    "explanation": "Should aggregate by revenue"
  }'
```

## Configuration

| Variable | Default | Description |
|---|---|---|
| `LLM_PROVIDER` | `ollama` | LLM backend: `ollama` or `openai` |
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `qwen2.5-coder` | Ollama model name |
| `OPENAI_API_KEY` | - | OpenAI API key |
| `OPENAI_MODEL` | `gpt-4o-mini` | OpenAI model name |
| `MAX_RETRIES` | `3` | Max SQL generation retries |
| `QUERY_TIMEOUT` | `30` | Query timeout in seconds |
| `MAX_RESULT_ROWS` | `500` | Maximum rows returned |
| `DEBUG` | `False` | Enable debug mode |

## Supported Databases

- PostgreSQL
- MySQL / MariaDB
- SQLite
- Any SQLAlchemy-compatible database

## License

MIT