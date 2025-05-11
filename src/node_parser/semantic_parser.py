"""语义节点解析器"""
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import BaseNode, TextNode
from typing import List, Optional, Sequence

class SemanticNodeParser(SentenceSplitter):
    """
    语义节点解析器
    
    用于处理默认情况下的文档，基于语义边界进行切分
    """
    
    def __init__(
        self,
        chunk_size: Optional[int] = 1024,
        chunk_overlap: Optional[int] = 200,
        include_metadata: bool = True,
        paragraph_separator: str = "\n\n",
        separator: str = " ",
    ):
        """
        初始化语义节点解析器
        
        Args:
            chunk_size: 块的大小（字符数）
            chunk_overlap: 块之间重叠的字符数
            include_metadata: 是否在节点中包含元数据
            paragraph_separator: 段落分隔符
            separator: 句子分隔符
        """
        super().__init__(
            chunk_size=chunk_size, 
            chunk_overlap=chunk_overlap,
            include_metadata=include_metadata,
            paragraph_separator=paragraph_separator,
            separator=separator,
        )
    
    def get_nodes_from_documents(
        self, documents: Sequence[BaseNode]
    ) -> List[TextNode]:
        """
        基于语义边界从文档中获取节点
        
        Args:
            documents: 要处理的文档序列
            
        Returns:
            List[TextNode]: 生成的节点列表
        """
        # 使用SentenceSplitter的基本功能，进行语义特定的解析
        nodes = super().get_nodes_from_documents(documents)
        
        # 标记这些节点为语义解析类型
        for node in nodes:
            # 确保metadata是字典类型
            if not isinstance(node.metadata, dict):
                node.metadata = {}
            node.metadata["parser_type"] = "semantic"
        
        return nodes 