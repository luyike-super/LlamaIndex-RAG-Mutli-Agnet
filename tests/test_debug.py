import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data_ingestion import run_ingestion_pipeline
from src.indices.index import build_tool_agents
import logging

# 配置详细日志
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        logger.info("开始调试测试...")
        
        # 获取文档查询引擎字典
        doc_engines = build_tool_agents()
        logger.info(f"成功加载 {len(doc_engines)} 个文档查询引擎")
        
        if not doc_engines:
            logger.error("没有加载到任何查询引擎，退出测试")
            sys.exit(1)
        
        # 测试简单查询
        for doc_id, engine in doc_engines.items():
            logger.info(f"\n===== 测试文档 {doc_id} =====")
            
            try:
                # 测试一个简单的查询
                test_query = "HCSL输出"
                logger.info(f"执行测试查询: {test_query}")
                
                response = engine.query(test_query)
                logger.info(f"查询成功，响应: {str(response)[:200]}...")
                
            except Exception as e:
                logger.error(f"查询失败: {e}", exc_info=True)
                
            # 只测试第一个引擎
            break
            
    except Exception as e:
        logger.error(f"调试测试失败: {e}", exc_info=True)
        sys.exit(1) 