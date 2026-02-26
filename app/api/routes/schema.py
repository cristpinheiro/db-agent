from fastapi import APIRouter, HTTPException, Query

from app.schemas.schema_info import ColumnInfo, ForeignKeyInfo, SchemaResponse, TableInfo
from app.services.connection_manager import connection_manager
from app.services.schema_discovery import schema_discovery

router = APIRouter()


@router.get("/{connection_name}", response_model=SchemaResponse)
async def get_schema(
    connection_name: str,
    force_refresh: bool = Query(False),
):
    try:
        engine = connection_manager.get_engine(connection_name)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    info = schema_discovery.discover(engine, connection_name, force=force_refresh)
    tables = []
    for table_name, tdata in info.get("tables", {}).items():
        columns = [
            ColumnInfo(
                name=c["name"],
                type=c["type"],
                nullable=c.get("nullable", True),
                primary_key=c.get("primary_key", False),
            )
            for c in tdata.get("columns", [])
        ]
        fks = [
            ForeignKeyInfo(
                columns=fk.get("columns", []),
                referred_table=fk.get("referred_table", ""),
                referred_columns=fk.get("referred_columns", []),
            )
            for fk in tdata.get("foreign_keys", [])
        ]
        tables.append(
            TableInfo(
                name=table_name,
                columns=columns,
                foreign_keys=fks,
                row_count_estimate=tdata.get("row_count_estimate"),
            )
        )
    return SchemaResponse(
        connection_name=connection_name,
        dialect=info.get("dialect", "unknown"),
        tables=tables,
    )
