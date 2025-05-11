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
import pickle
from config.config_rag import DOCUMENT_CONFIG
from llama_index.core.storage.docstore import SimpleDocumentStore

# 定义持久化存储路径
STORAGE_DIR = "store/docs"

def ensure_storage_dir_exists():
    """确保存储目录存在"""
    os.makedirs(STORAGE_DIR, exist_ok=True)

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

def save_nodes_to_disk(nodes: List[BaseNode], filename: str = "processed_nodes.pkl"):
    """将处理后的节点持久化到磁盘"""
    ensure_storage_dir_exists()
    filepath = os.path.join(STORAGE_DIR, filename)
    
    try:
        # 使用pickle保存节点
        with open(filepath, "wb") as f:
            pickle.dump(nodes, f)
        print(f"已将节点保存至: {filepath}")
        return True
    except Exception as e:
        print(f"保存节点时出错: {e}")
        return False
        
def load_nodes_from_disk(filename: str = "processed_nodes.pkl") -> Optional[List[BaseNode]]:
    """从磁盘加载持久化的节点"""
    filepath = os.path.join(STORAGE_DIR, filename)
    
    if not os.path.exists(filepath):
        print(f"找不到节点文件: {filepath}")
        return None
        
    try:
        with open(filepath, "rb") as f:
            nodes = pickle.load(f)
        print(f"已从 {filepath} 加载 {len(nodes)} 个节点")
        return nodes
    except Exception as e:
        print(f"加载节点时出错: {e}")
        return None

def create_document_store(nodes: List[BaseNode]) -> SimpleDocumentStore:
    """创建并返回文档存储"""
    doc_store = SimpleDocumentStore()
    doc_store.add_documents(nodes)
    return doc_store

def run_ingestion_pipeline(documents=None) -> List[BaseNode]:
    """
    运行数据摄入管道处理文档，并持久化到磁盘
    
    Args:
        documents: 要处理的文档，默认为None
    Returns:
        处理后的节点列表
    """
    # 首先尝试从磁盘加载持久化的节点
    loaded_nodes = load_nodes_from_disk()
    
    # 如果找到了持久化的节点，直接返回
    if loaded_nodes is not None:
        print("已加载持久化的节点数据")
        return loaded_nodes
    
    # 如果没有持久化节点，处理文档
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
    
    # 将处理后的节点持久化保存
    save_nodes_to_disk(nodes)
    
    # 创建并返回文档存储
    doc_store = create_document_store(nodes)
    print(f"已创建文档存储，包含 {len(nodes)} 个节点")
    
    return nodes

# 方便直接运行此文件时测试
if __name__ == "__main__":
    nodes = run_ingestion_pipeline()
    print(f"处理完成，共生成 {len(nodes)} 个节点")