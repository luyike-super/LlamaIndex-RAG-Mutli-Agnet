from pydantic import BaseModel, Field
from typing import List, Optional


class Document(BaseModel):
    """文档模型"""
    id: Optional[str] = None
    content: str
    metadata: dict = Field(default_factory=dict)


class IngestionResponse(BaseModel):
    """文档摄入响应"""
    success: bool
    message: str
    document_ids: List[str] = []


class QueryRequest(BaseModel):
    """查询请求"""
    query: str
    top_k: int = 3
    

class SourceNode(BaseModel):
    """源节点信息"""
    text: str
    source: str
    score: Optional[float] = None


class QueryResponse(BaseModel):
    """查询响应"""
    answer: str
    sources: List[SourceNode] = []
    
    
class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str
    version: str 