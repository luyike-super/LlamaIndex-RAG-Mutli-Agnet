import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data_ingestion import run_ingestion_pipeline
from src.indices.index import test_load_docs
if __name__ == "__main__":
    docs = test_load_docs()
    print(docs)