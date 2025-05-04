"""
数据清洗    
"""

from llama_index.core.schema import TransformComponent
from llama_index.core.bridge.pydantic import Field

from src.utils import transform_logger

class DataCleanerTransform(TransformComponent):
    """数据清洗"""
    def __call__(self, nodes, **kwargs):
        transform_logger.info("开始数据清洗" + str(len(nodes)) + "条数据")
        return nodes    