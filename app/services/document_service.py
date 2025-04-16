from typing import List, Optional, Dict, Any
from app.models.models import Document

class DocumentService:
    """文档服务类"""
    
    @staticmethod
    async def create_document(title: str, content: str, file_path: Optional[str] = None, 
                             file_type: Optional[str] = None, metadata: Dict[str, Any] = None) -> Document:
        """创建文档"""
        return await Document.create(
            title=title,
            content=content,
            file_path=file_path,
            file_type=file_type,
            metadata=metadata or {}
        )
    
    @staticmethod
    async def get_document(document_id: int) -> Optional[Document]:
        """获取文档"""
        return await Document.filter(id=document_id).first()
    
    @staticmethod
    async def get_documents(limit: int = 10, offset: int = 0) -> List[Document]:
        """获取文档列表"""
        return await Document.all().offset(offset).limit(limit)
    
    @staticmethod
    async def update_document(document_id: int, **kwargs) -> Optional[Document]:
        """更新文档"""
        document = await DocumentService.get_document(document_id)
        if document:
            await document.update_from_dict(kwargs).save()
            return document
        return None
    
    @staticmethod
    async def delete_document(document_id: int) -> bool:
        """删除文档"""
        document = await DocumentService.get_document(document_id)
        if document:
            await document.delete()
            return True
        return False 