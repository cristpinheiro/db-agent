from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.connection_manager import connection_manager
from app.services.schema_discovery import schema_discovery
from app.services.glossary.admin_glossary import admin_glossary
from app.services.glossary.feedback_glossary import feedback_glossary
from app.services.glossary.glossary_compositor import glossary_compositor

router = APIRouter()


class TermRequest(BaseModel):
    term: str
    definition: str
    sql_pattern: Optional[str] = ""
    notes: Optional[str] = ""


class FeedbackRequest(BaseModel):
    question: str
    chosen_label: str
    chosen_sql: str
    all_options: Optional[list] = []


class CorrectionRequest(BaseModel):
    question: str
    original_sql: str
    corrected_sql: str
    explanation: Optional[str] = ""


@router.post("/{connection_name}/terms")
async def add_term(connection_name: str, body: TermRequest):
    admin_glossary.add_term(
        connection_name, body.term, body.definition,
        body.sql_pattern or "", body.notes or ""
    )
    return {"message": "Term added"}


@router.get("/{connection_name}/terms")
async def list_terms(connection_name: str):
    return {"terms": admin_glossary.get_terms(connection_name)}


@router.delete("/{connection_name}/terms/{term}")
async def remove_term(connection_name: str, term: str):
    removed = admin_glossary.remove_term(connection_name, term)
    if not removed:
        raise HTTPException(status_code=404, detail="Term not found")
    return {"message": "Term removed"}


@router.post("/{connection_name}/feedback")
async def submit_feedback(connection_name: str, body: FeedbackRequest):
    feedback_glossary.record_preference(
        connection_name, body.question, body.chosen_label,
        body.chosen_sql, body.all_options or []
    )
    return {"message": "Feedback recorded"}


@router.post("/{connection_name}/correction")
async def submit_correction(connection_name: str, body: CorrectionRequest):
    feedback_glossary.record_correction(
        connection_name, body.question, body.original_sql,
        body.corrected_sql, body.explanation or ""
    )
    return {"message": "Correction recorded"}


@router.get("/{connection_name}/full")
async def get_full_glossary(connection_name: str):
    try:
        engine = connection_manager.get_engine(connection_name)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    prompt = glossary_compositor.build_glossary_prompt(engine, connection_name)
    return {"glossary_prompt": prompt}
