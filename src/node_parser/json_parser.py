"""JSON文档节点解析器"""
from llama_index.core.node_parser import SimpleNodeParser
from llama_index.core.schema import BaseNode, TextNode
from typing import List, Optional, Sequence

class JSONNodeParser(SimpleNodeParser):
    """
    JSON文档节点解析器
    
    专门用于解析JSON格式的文档
    """
    
    def __init__(
        self,
        chunk_size: Optional[int] = 1024,
        chunk_overlap: Optional[int] = 20,
        include_metadata: bool = True,
    ):
        """
        初始化JSON节点解析器
        
        Args:
            chunk_size: 块的大小（字符数）
            chunk_overlap: 块之间重叠的字符数
            include_metadata: 是否在节点中包含元数据
        """
        super().__init__(
            chunk_size=chunk_size, 
            chunk_overlap=chunk_overlap,
            include_metadata=include_metadata,
        )
    
    def get_nodes_from_documents(
        self, documents: Sequence[BaseNode]
    ) -> List[TextNode]:
        """
        从JSON文档中获取节点
        
        Args:
            documents: 要处理的文档序列
            
        Returns:
            List[TextNode]: 生成的节点列表
        """
        # 使用SimpleNodeParser的基本功能，进行JSON特定的解析
        nodes = super().get_nodes_from_documents(documents)
        
        # 在这里可以添加JSON特定的处理逻辑
        # 例如，标记这些节点为JSON类型
        for node in nodes:
            # 确保metadata是字典类型
            if not isinstance(node.metadata, dict):
                node.metadata = {}
            node.metadata["parser_type"] = "json"
        
        return nodes 