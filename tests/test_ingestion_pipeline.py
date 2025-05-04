import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


import unittest
from unittest.mock import patch, MagicMock
from src.transformations.category_extract import ClassifyExtract



from llama_index.core import Document
from llama_index.core.ingestion import IngestionPipeline
from src.transformations.data_cleaner_transform import DataCleanerTransform
from src.data_ingestion.reader import default_reader
from llama_index.core.node_parser import SentenceSplitter

if __name__ == "__main__":
         # 创建管道
        pipeline = IngestionPipeline(
            transformations=[ClassifyExtract()]
        )
        
        # 运行管道
        nodes = pipeline.run(documents=default_reader)
        print(nodes)