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
from config.config_rag import DOCUMENT_CONFIG

def create_pipeline():
    """创建并返回数据摄入管道"""
    return IngestionPipeline(
        transformations=[
            DataCleanerTransform(),  # 数据清洗，实例化类
            DocumentURLNormalizerTransform(),  # 文档URL规范化，实例化类
            CategoryExtract(),  # 分类提取，实例化类
            DocsSummarizerTransform()  # 文档摘要，实例化类
        ]
    )

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
    nodes = run_ingestion_pipeline()
    print(f"处理完成，共生成 {len(nodes)} 个节点")