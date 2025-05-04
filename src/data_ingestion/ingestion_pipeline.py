from llama_index.core import Document
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import TokenTextSplitter
from llama_index.core.extractors import KeywordExtractor
from llama_index.embeddings.openai import OpenAIEmbedding
from src.transformations import (DataCleanerTransform, DocsSummarizerTransform, DocumentURLNormalizerTransform,CategoryExtract)
from src.models import EmbeddingFactory, EmbeddingProviderType
from llama_index.core.node_parser import SentenceSplitter
from src.data_ingestion.reader import default_reader
from typing import List, Optional
from llama_index.core.schema import BaseNode

def create_pipeline():
    """创建并返回数据摄入管道"""
    return IngestionPipeline(
        transformations=[
            DataCleanerTransform(),  # 数据清洗，实例化类
            DocumentURLNormalizerTransform(),  # 文档URL规范化，实例化类
            CategoryExtract()  # 分类提取，实例化类
        ]
    )

def run_ingestion_pipeline(documents=None) -> List[BaseNode]:
    """
    运行数据摄入管道处理文档
    
    Args:
        documents: 要处理的文档，默认使用default_reader
        
    Returns:
        处理后的节点列表
    """
    if documents is None:
        documents = default_reader
        
    pipeline = create_pipeline()
    return pipeline.run(documents=documents)

# 方便直接运行此文件时测试
if __name__ == "__main__":
    nodes = run_ingestion_pipeline()
    print(f"处理完成，共生成 {len(nodes)} 个节点")