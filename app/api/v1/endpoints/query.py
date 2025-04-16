from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.services.rag_service import RAGService, get_rag_service

router = APIRouter()

class QueryRequest(BaseModel):
    query: str
    
class QueryResponse(BaseModel):
    answer: str
    sources: list[str] = []

@router.post("/", response_model=QueryResponse)
async def query(
    request: QueryRequest,
    rag_service: RAGService = Depends(get_rag_service)
):
    try:
        result = rag_service.query(request.query)
        return {
            "answer": result.response,
            "sources": [node.node.metadata.get("source", "") for node in result.source_nodes]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询错误: {str(e)}") 