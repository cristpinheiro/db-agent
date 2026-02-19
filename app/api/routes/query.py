from fastapi import APIRouter, HTTPException

from app.schemas.query import QueryRequest, QueryResponse
from app.services.agent import agent

router = APIRouter()


@router.post("/", response_model=QueryResponse)
async def ask_question(body: QueryRequest):
    try:
        result = agent.process_question(body.question, body.connection_name)
        return QueryResponse(**result)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
