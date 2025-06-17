import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data_ingestion import run_ingestion_pipeline
from src.indices.index import build_tool_agents
if __name__ == "__main__":
    # 获取文档查询引擎字典
    doc_engines = build_tool_agents()
    print(f"成功加载 {len(doc_engines)} 个文档查询引擎")
    
    # 遍历文档ID和对应的查询引擎
    for doc_id, engine in doc_engines.items():
        print(f"\n===== 文档 {doc_id} 的查询结果 =====")
        # 调用查询引擎的query方法
        response = engine.query(" 如何使用硬件控制模式，把输出类型设置为 HCSL")
        print(response)
