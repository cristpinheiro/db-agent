from fastapi import APIRouter, HTTPException

from app.schemas.connection import ConnectionCreate, ConnectionListResponse, ConnectionResponse
from app.services.connection_manager import connection_manager

router = APIRouter()


@router.post("/", response_model=ConnectionResponse)
async def register_connection(body: ConnectionCreate):
    try:
        info = connection_manager.register(body.name, body.url)
        return ConnectionResponse(**info)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/", response_model=ConnectionListResponse)
async def list_connections():
    connections = connection_manager.list_connections()
    return ConnectionListResponse(connections=[ConnectionResponse(**c) for c in connections])


@router.delete("/{name}")
async def remove_connection(name: str):
    try:
        connection_manager.remove(name)
        return {"message": f"Connection '{name}' removed"}
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
