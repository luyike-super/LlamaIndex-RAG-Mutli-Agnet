from os.path import relpath, splitext

from llama_index.core.schema import TransformComponent
from llama_index.core.bridge.pydantic import Field

from src.utils import transform_logger

"""
文档路径进行标准化： 比如"c:/aaa/bbb/data/docs/example.md" 转换为 "data/example.md"
"""

class DocumentURLNormalizerTransform(TransformComponent):

  data_path: str = Field(
    default='./data',
    description='数据目录的相对路径'
  )

  def __call__(self, nodes, **kwargs):
    for node in nodes:
      node.metadata["file_path"], _ = splitext(relpath(node.metadata['file_path'], self.data_path+"/docs"))
      transform_logger.debug("文档路径标准化完成  " + node.metadata["file_path"])
    return nodes