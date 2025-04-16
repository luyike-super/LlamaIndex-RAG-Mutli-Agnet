from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

router = APIRouter()

class QueryRequest(BaseModel):
    query: str
    
class QueryResponse(BaseModel):
    answer: str
    sources: list[str] = []

@router.post("/", response_model=QueryResponse)
async def query(
    request: QueryRequest
):
    return {"answer": "Hello, World!", "sources": []}