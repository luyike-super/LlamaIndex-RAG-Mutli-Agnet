from typing import Optional
import os
from llama_index import VectorStoreIndex, ServiceContext, StorageContext, load_index_from_storage
from llama_index.llms import OpenAI
from llama_index.query_engine import RetrieverQueryEngine
from app.core.config import settings

class RAGService:
    def __init__(self, index_dir: Optional[str] = None):
        self.index_dir = index_dir or settings.INDEX_DIR
        self.index = self._load_or_create_index()
        
    def _load_or_create_index(self):
        """加载或创建向量存储索引"""
        try:
            if os.path.exists(self.index_dir):
                # 从磁盘加载现有索引
                storage_context = StorageContext.from_defaults(persist_dir=self.index_dir)
                return load_index_from_storage(storage_context)
            else:
                # 暂时创建一个空索引
                return VectorStoreIndex([])
        except Exception as e:
            print(f"加载索引失败: {str(e)}")
            return VectorStoreIndex([])
    
    def query(self, query_text: str):
        """执行查询并返回响应"""
        query_engine = self.index.as_query_engine()
        return query_engine.query(query_text)

# 依赖项，用于FastAPI依赖注入
_rag_service_instance = None

def get_rag_service():
    """获取RAG服务单例"""
    global _rag_service_instance
    if _rag_service_instance is None:
        _rag_service_instance = RAGService()
    return _rag_service_instance 