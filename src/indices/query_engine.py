from typing import Dict, List
from llama_index.core.schema import TextNode
from llama_index.core.callbacks import CallbackManager
from llama_index.core.node_parser import NodeParser
from llama_index.core import VectorStoreIndex
from src.NodeParser import (
    CustomMarkdownNodeParser,
    JSONNodeParser,
    WordNodeParser,
    SemanticNodeParser
)
import os


def build_query_engine(docs: list[TextNode]) -> Dict:
    """
    构建文档查询引擎。
    根据文档类别（doc.metadata.category）对查询引擎进行分组。
    
    Args:
        storage_dir: 存储目录路径
        docs: 文档列表
        callback_manager: 回调管理器
    
    Returns:
        Dict: 包含两个字典: 
            - 'by_id': 以文档ID为键的查询引擎字典
            - 'by_category': 以类别为键、查询引擎列表为值的字典
    """

    # Settings.callback_manager = callback_manager
    # service_context = ServiceContext.from_defaults(llm=llm)

    # 构建查询引擎字典 - 按ID索引
    engines_by_id = {}
    
    # 构建查询引擎字典 - 按类别分组
    engines_by_category = {}
    

    for idx, doc in enumerate(docs):
        all_nodes = []
        # 根据文档类型选择适当的解析器
        node_parser = get_parser_for_document(doc)
        
        # 使用选择的解析器处理文档
        nodes = node_parser.get_nodes_from_documents([doc])
        all_nodes.extend(nodes)
        vector_index = VectorStoreIndex(all_nodes)
        vector_query_engine = vector_index.as_query_engine()
        
        # 存储到ID映射
        engines_by_id[doc.id_] = vector_query_engine
        
        # 获取文档类别
        category = "未分类"
        if hasattr(doc, 'metadata') and 'category' in doc.metadata:
            category = doc.metadata['category']
        
        # 将查询引擎添加到对应类别
        if category not in engines_by_category:
            engines_by_category[category] = []
        engines_by_category[category].append(vector_query_engine)

    return {
        "by_id": engines_by_id,
        "by_category": engines_by_category
    }

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
    if hasattr(doc, 'metadata') and 'file_name' in doc.metadata:
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