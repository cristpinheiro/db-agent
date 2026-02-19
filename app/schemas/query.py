from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class QueryRequest(BaseModel):
    question: str
    connection_name: str
    strategy: str = "auto"


class PerspectiveResult(BaseModel):
    label: str
    interpretation: Optional[str] = None
    sql_query: str
    sql_executed: Optional[str] = None
    results: List[Dict[str, Any]]
    row_count: int
    execution_time: float
    success: bool
    error: Optional[str] = None


class InterpretationOption(BaseModel):
    label: str
    meaning: str


class QueryResponse(BaseModel):
    question: str
    needs_clarification: bool = False
    ambiguity_detected: bool = False
    ambiguity_type: Optional[str] = None
    message: Optional[str] = None
    interpretations: List[InterpretationOption] = []
    perspectives: List[PerspectiveResult] = []
    dialect: Optional[str] = None
    retry_count: int = 0
    success: bool
    error_message: Optional[str] = None
    mapping_used: bool = False
