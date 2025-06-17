from llama_index.core import Document
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import TokenTextSplitter
from llama_index.core.extractors import KeywordExtractor
from llama_index.embeddings.openai import OpenAIEmbedding
from src.transformations import (DataCleanerTransform, DocsSummarizerTransform, DocumentURLNormalizerTransform,CategoryExtract)
from src.models import EmbeddingFactory, EmbeddingProviderType
from llama_index.core.node_parser import SentenceSplitter
from src.data_ingestion.reader import default_reader
from typing import List, Optional, Tuple
from llama_index.core.schema import BaseNode
import os
from config.config_rag import DOCUMENT_CONFIG, CHUNKING_CONFIG
from src.node_parser.node_parser_tool import get_parser_for_document

def create_pipeline_with_chunking():
    """创建包含文档切分功能的数据摄入管道"""
    
    # 获取默认配置用于切分
    default_config = CHUNKING_CONFIG.get("default", {
        "chunk_size": 1024,
        "chunk_overlap": 200,
        "separator": " "
    })
    
    return IngestionPipeline(
        transformations=[
            DataCleanerTransform(),          # 数据清洗，实例化类
            DocumentURLNormalizerTransform(), # 文档URL规范化，实例化类
            CategoryExtract(),               # 分类提取，实例化类
            DocsSummarizerTransform(),       # 文档摘要，实例化类
            # 添加文档切分步骤
            SentenceSplitter(
                chunk_size=default_config["chunk_size"],
                chunk_overlap=default_config["chunk_overlap"],
                separator=default_config["separator"]
            )
        ]
    )

def create_pipeline():
    """创建并返回数据摄入管道（保持向后兼容）"""
    return IngestionPipeline(
        transformations=[
            DataCleanerTransform(),  # 数据清洗，实例化类
            DocumentURLNormalizerTransform(),  # 文档URL规范化，实例化类
            CategoryExtract(),  # 分类提取，实例化类
            DocsSummarizerTransform()  # 文档摘要，实例化类
        ]
    )

def run_ingestion_pipeline_with_smart_chunking(documents=None) -> List[BaseNode]:
    """
    运行数据摄入管道处理文档，使用智能切分
    
    Args:
        documents: 要处理的文档，默认为None
    Returns:
        处理后的节点列表
    """
    # 如果没有提供文档，从配置中获取
    if documents is None:
        # 从配置中获取文档目录路径
        input_dir = DOCUMENT_CONFIG.get("input_dir", "data")
        recursive = DOCUMENT_CONFIG.get("recursive", True)
        supported_file_types = DOCUMENT_CONFIG.get("supported_file_types", [".md", ".txt"])
        
        print(f"使用配置从 {input_dir} 读取文档，递归={recursive}，支持的文件类型={supported_file_types}")
        documents = default_reader
    
    # 首先运行基础管道（不包含切分）
    base_pipeline = create_pipeline()
    processed_docs = base_pipeline.run(documents=documents)
    
    print(f"基础处理完成，处理了 {len(processed_docs)} 个文档")
    
    # 然后根据文档类型进行智能切分
    all_chunks = []
    
    for doc in processed_docs:
        try:
            # 根据文档类型选择合适的解析器
            parser = get_parser_for_document(doc)
            
            # 执行切分
            chunks = parser.get_nodes_from_documents([doc])
            
            print(f"文档 {doc.metadata.get('file_name', 'Unknown')} 切分为 {len(chunks)} 个块")
            
            all_chunks.extend(chunks)
            
        except Exception as e:
            print(f"处理文档 {doc.metadata.get('file_name', 'Unknown')} 时出错: {e}")
            # 如果切分失败，保留原文档
            all_chunks.append(doc)
    
    print(f"智能切分完成，总共生成 {len(all_chunks)} 个节点")
    return all_chunks

def run_ingestion_pipeline(documents=None) -> List[BaseNode]:
    """
    运行数据摄入管道处理文档
    
    Args:
        documents: 要处理的文档，默认为None
    Returns:
        处理后的节点列表
    """
    # 如果没有提供文档，从配置中获取
    if documents is None:
        # 从配置中获取文档目录路径
        input_dir = DOCUMENT_CONFIG.get("input_dir", "data")
        recursive = DOCUMENT_CONFIG.get("recursive", True)
        supported_file_types = DOCUMENT_CONFIG.get("supported_file_types", [".md", ".txt"])
        
        print(f"使用配置从 {input_dir} 读取文档，递归={recursive}，支持的文件类型={supported_file_types}")
        documents = default_reader
        
    # 处理文档
    pipeline = create_pipeline()
    nodes = pipeline.run(documents=documents)
    
    print(f"已处理文档，生成 {len(nodes)} 个节点")
    return nodes

# 方便直接运行此文件时测试
if __name__ == "__main__":
    # 测试智能切分版本
    nodes = run_ingestion_pipeline_with_smart_chunking()
    print(f"智能切分处理完成，共生成 {len(nodes)} 个节点")