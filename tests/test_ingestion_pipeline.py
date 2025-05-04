import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data_ingestion import run_ingestion_pipeline
from src.indices.index import test_load_docs
if __name__ == "__main__":
    # 获取文档查询引擎字典
    doc_engines = test_load_docs()
    print(f"成功加载 {len(doc_engines)} 个文档查询引擎")
    
    # 遍历文档ID和对应的查询引擎
    for doc_id, engine in doc_engines.items():
        print(f"\n===== 文档 {doc_id} 的查询结果 =====")
        # 调用查询引擎的query方法
        response = engine.query("小行星是什么?")
        print(response)
