from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.connection_manager import connection_manager
from app.services.schema_discovery import schema_discovery
from app.services.schema_mapping.mapping_store import mapping_store
from app.services.schema_mapping.auto_mapper import AutoMapper

router = APIRouter()


class AutoMapRequest(BaseModel):
    erp_hint: Optional[str] = ""


class TableMappingRequest(BaseModel):
    real_table: str
    friendly_name: str
    description: Optional[str] = ""


class ColumnMappingRequest(BaseModel):
    real_table: str
    real_column: str
    friendly_name: str
    description: Optional[str] = ""
    business_type: Optional[str] = ""


@router.post("/{connection_name}/auto")
async def auto_generate_mapping(connection_name: str, body: AutoMapRequest):
    try:
        engine = connection_manager.get_engine(connection_name)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    schema_info = schema_discovery.discover(engine, connection_name)
    mapper = AutoMapper()
    mapping = mapper.generate_mapping(schema_info, erp_hint=body.erp_hint or "")
    mapping_store.set_mapping(connection_name, mapping)
    return {"message": "Mapping generated", "mapping": mapping}


@router.get("/{connection_name}")
async def get_mapping(connection_name: str):
    m = mapping_store.get_mapping(connection_name)
    if m is None:
        return {"mapping": None}
    return {"mapping": m}


@router.put("/{connection_name}/full")
async def set_full_mapping(connection_name: str, mapping: dict):
    mapping_store.set_mapping(connection_name, mapping)
    return {"message": "Mapping updated"}


@router.put("/{connection_name}/tables")
async def map_table(connection_name: str, body: TableMappingRequest):
    mapping_store.update_table(
        connection_name, body.real_table, body.friendly_name, body.description or ""
    )
    return {"message": "Table mapping updated"}


@router.put("/{connection_name}/columns")
async def map_column(connection_name: str, body: ColumnMappingRequest):
    mapping_store.update_column(
        connection_name,
        body.real_table,
        body.real_column,
        body.friendly_name,
        body.description or "",
        body.business_type or "",
    )
    return {"message": "Column mapping updated"}
