import os
import shutil
from app.utils.logger import logger

class IndexConfig:
    # 持久化目录
    PERSIST_DIR = "./data/index"

def clean_doc_fn():
    # 获取文档路径
    doc_path = IndexConfig.PERSIST_DIR
    
    # 确保目录存在
    if not os.path.exists(doc_path):
        logger.warning(f"目录 {doc_path} 不存在")
        return
        
    try:
        # 删除目录下的所有内容
        for item in os.listdir(doc_path):
            item_path = os.path.join(doc_path, item)
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)
        logger.info(f"成功清理目录 {doc_path} 下的所有内容")
    except Exception as e:
        logger.error(f"清理目录时出错: {str(e)}")

if __name__ == "__main__":
    clean_doc_fn()
