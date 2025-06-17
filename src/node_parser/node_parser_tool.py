import os
from llama_index.core.node_parser import NodeParser
from llama_index.core.schema import TextNode
from config.config_rag import CHUNKING_CONFIG
from src.node_parser import (
    CustomMarkdownNodeParser,
    JSONNodeParser,
    WordNodeParser,
    SemanticNodeParser
)

def get_parser_for_document(doc: TextNode) -> NodeParser:
    """
    根据文档类型选择适当的解析器，并使用优化的分块配置
    
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
    
    # 根据扩展名选择解析器和配置
    if file_ext in ['.md', '.mdx']:
        config = CHUNKING_CONFIG.get("markdown", CHUNKING_CONFIG["default"])
        return CustomMarkdownNodeParser(
            chunk_size=config["chunk_size"],
            chunk_overlap=config["chunk_overlap"],
            separator=config["separator"]
        )
    elif file_ext in ['.json']:
        config = CHUNKING_CONFIG.get("json", CHUNKING_CONFIG["default"])
        return JSONNodeParser(
            chunk_size=config["chunk_size"],
            chunk_overlap=config["chunk_overlap"]
        )
    elif file_ext in ['.doc', '.docx']:
        config = CHUNKING_CONFIG.get("docx", CHUNKING_CONFIG["default"])
        return WordNodeParser(
            chunk_size=config["chunk_size"],
            chunk_overlap=config["chunk_overlap"]
        )
    else:
        # 默认使用语义解析器
        config = CHUNKING_CONFIG.get("default", CHUNKING_CONFIG["default"])
        return SemanticNodeParser(
            chunk_size=config["chunk_size"],
            chunk_overlap=config["chunk_overlap"],
            separator=config["separator"]
        )