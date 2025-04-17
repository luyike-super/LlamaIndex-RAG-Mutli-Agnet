"""
索引管理工具 - 用于处理文档更新时的索引操作
"""
import logging
from importlib import import_module
from llama_index.core.schema import TransformComponent
from llama_index.core.storage.docstore.types import BaseDocumentStore
from pydantic import Field
# 配置日志
logger = logging.getLogger()

class DeleteOldIndex(TransformComponent):
    """定时启动，如果文档有更新，则删除所有索引"""
    # 文档存储
    documentStore: BaseDocumentStore = Field(description="文档存储")

    # 根据文档ID删除索引 
    clean_doc_fn: callable = Field(default=lambda _: None, description="根据文档ID删除索引的函数")
    
    def __call__(self, nodes, **kwargs):
        """如果有文档
        
        Args:
            nodes: 待处理的节点
            
        Returns:
            需要处理的nodes
        """
        try:
            assert self.documentStore is not None
            # 获取documentStore中的所有文档ID,使用set
            doc_ids = set(self.documentStore.get_all_document_hashes().keys())
            
            # 用于存储当前nodes的文档ID的set
            nodes_all_doc_ids = set()

            # 用于存储需要进一步处理的nodes列表
            need_process_nodes = []

            for node in nodes:
                # 优先获取node的ref_doc_id
                doc_id = node.ref_doc_id if node.ref_doc_id else node.doc_id
                
                # 存入全部文档
                nodes_all_doc_ids.add(doc_id)

                # 获取node的文档ID的hash
                doc_id_hash = self.documentStore.get_document_hash(doc_id)

                # 如果 doc_id_hash 不存在，说明是新文档，需要进一步处理
                # 如果 doc_id_hash 且不等于node.hash 存在，说明更新了，需要更新documentStore， 并删除旧的索引
                # 其他情况，说明是旧文档，不需要处理

                if doc_id_hash is None:
                    # 只更新元数据，便于追踪
                    self.documentStore.set_document_hashes({doc_id: node.hash})
                    need_process_nodes.append(node)
                elif doc_id_hash != node.hash:
                    # 删除之前所有关联的文档
                    self.documentStore.delete_ref_doc(doc_id,raise_error=False)
                    # 设置新的hash， 便于追踪
                    self.documentStore.set_document_hashes({doc_id: node.hash})
                    need_process_nodes.append(node)
                    logger.info(f"文档 {doc_id} 已更新，将删除旧索引")
                else:
                    # 旧文档，不需要处理
                    logger.debug(f"文档 {doc_id} 未变更，无需处理")
            
            # 找出需要删除的文档ID（在文档存储中但不在当前nodes中的）
            docs_to_delete = doc_ids - nodes_all_doc_ids
            # 执行删除
            for doc_id in docs_to_delete:
                self.clean_fn(doc_id)
            return need_process_nodes
        
        except Exception as e:
            logger.error(f"处理索引时出错: {str(e)}")
            # 发生错误时返回原始节点
            return nodes
