import os
from llama_index.core.node_parser import NodeParser
from llama_index.core.schema import TextNode
from src.node_parser import (
    CustomMarkdownNodeParser,
    JSONNodeParser,
    WordNodeParser,
    SemanticNodeParser
)

def get_parser_for_document(doc: TextNode) -> NodeParser:
    """
    根据文档类型选择适当的解析器
    
    Args:
        doc: 文档节点
        
    Returns:
        NodeParser: 适合该文档类型的解析器
    """
    # 从文件名或元数据中获取文件扩展名
    file_ext = ""
    # 确保metadata是字典类型
    if not isinstance(doc.metadata, dict):
        doc.metadata = {}
        
    if 'file_name' in doc.metadata:
        file_name = doc.metadata['file_name']
        _, file_ext = os.path.splitext(file_name)
        file_ext = file_ext.lower()
    
    # 根据扩展名选择解析器
    if file_ext in ['.md', '.mdx']:
        return CustomMarkdownNodeParser()
    elif file_ext in ['.json']:
        return JSONNodeParser()
    elif file_ext in ['.doc', '.docx']:
        return WordNodeParser()
    else:
        # 默认使用语义解析器
        return SemanticNodeParser()