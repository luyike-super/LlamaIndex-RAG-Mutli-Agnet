from llama_index.core import Document
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import TokenTextSplitter
from llama_index.core.extractors import KeywordExtractor
from llama_index.embeddings.openai import OpenAIEmbedding
from src.transformations import (DataCleanerTransform, DocsSummarizerTransform,  DocumentURLNormalizerTransform)
from src.models import EmbeddingFactory, EmbeddingProviderType
from llama_index.core.node_parser import SentenceSplitter



# 创建文档
documents = [Document(text="您的文档内容")]

# 定义转换组件
pipeline = IngestionPipeline(
    documents=documents,
    transformations=[
        DataCleanerTransform,  # 数据清洗
        SentenceSplitter(),  # 句子分割
        
        KeywordExtractor(keywords=5),  # 提取关键词
        OpenAIEmbedding()  # 生成嵌入向量
    ]
    )

# 运行管道
nodes = pipeline.run(documents=documents)