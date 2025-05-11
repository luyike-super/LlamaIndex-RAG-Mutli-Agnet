from llama_index.core.schema import TransformComponent
from llama_index.core.bridge.pydantic import Field
import os
import re

from src.utils import transform_logger

class CategoryExtract(TransformComponent):
    """
    从文件名中提取类别并将其存储在节点元数据中。
    例如：从类型_文件名.docx中提取"类型"作为类别。
    """
    
    def __call__(self, nodes, **kwargs):
        """
        获取原始文件名，获取类别后，存入元数据，比如：类型_文件名.docx，提取的是类别     
        """
        transform_logger.info(f"正在处理 {len(nodes)} 个节点的类别提取")
        
        for node in nodes:
            # 确保metadata是字典类型
            if not isinstance(node.metadata, dict):
                node.metadata = {}
                
            if 'file_name' in node.metadata:
                file_name = node.metadata['file_name']
                
                # 尝试从文件名中提取类别（假设格式为：类别_文件名.扩展名）
                category_match = re.match(r'^([^_]+)_.*', os.path.basename(file_name))
                
                if category_match:
                    category = category_match.group(1)
                    # 将类别添加到节点的元数据中
                    node.metadata['category'] = category
                    transform_logger.debug(f"为文件 {file_name} 提取的类别: {category}")
                else:
                    transform_logger.warning(f"无法从文件 {file_name} 提取类别")
            else:
                transform_logger.warning(f"节点缺少文件名元数据")
                
        transform_logger.info(f"类别提取完成")
        return nodes    