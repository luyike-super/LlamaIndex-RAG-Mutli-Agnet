from llama_index.core.settings import Settings
from llama_index.core.schema import TextNode
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.objects import ObjectIndex
from llama_index.core.storage.storage_context import StorageContext
from llama_index.core.indices import VectorStoreIndex
from llama_index.core.indices.loading import load_index_from_storage
from llama_index.core.agent import ReActAgent
from src.models import LLMFactory, EmbeddingFactory, LLMProviderType, EmbeddingProviderType
from src.data_ingestion.ingestion_pipeline import run_ingestion_pipeline
from typing import List, Dict, Optional, Any
from llama_index.core.objects.tool_node_mapping import SimpleToolNodeMapping
from llama_index.core.callbacks import CallbackManager
from llama_index.core.node_parser import NodeParser
from src.node_parser.node_parser_tool import get_parser_for_document
import os
import logging
import time
import requests
from llama_index.core.schema import BaseNode
from llama_index.core.storage.docstore import SimpleDocumentStore, DocumentStore

# 配置基本日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('llama_kb.indices')

# 初始化模型
try:
    # 检查网络连接
    requests.get("https://www.baidu.com", timeout=5)
    # 正常初始化
    Settings.llm = LLMFactory.create_llm(LLMProviderType.QIANWENOPENAI)
    Settings.embed_model = EmbeddingFactory.create_embedding(EmbeddingProviderType.DASHSCOPE)
except Exception as e:
    logger.warning(f"网络连接检查失败: {e}")

# 定义持久化存储路径
VECTOR_CACHE_DIR = "store/vector_indices"
DOC_STORE_DIR = "store/docstore"

# 创建StorageContextManager单例类
class StorageContextManager:
    """StorageContext的单例管理器，用于全局管理和访问存储上下文"""
    
    _instance = None
    _storage_contexts = {}  # 存储多个存储上下文的字典
    
    @classmethod
    def get_instance(cls):
        """获取单例实例"""
        if cls._instance is None:
            cls._instance = StorageContextManager()
        return cls._instance
    
    def get_default_context(self) -> Optional[StorageContext]:
        """获取默认存储上下文"""
        return self._storage_contexts.get("default")
    
    def set_default_context(self, context: StorageContext):
        """设置默认存储上下文"""
        self._storage_contexts["default"] = context
        logger.info("已设置默认存储上下文")
    
    def get_context(self, name: str) -> Optional[StorageContext]:
        """获取指定名称的存储上下文"""
        return self._storage_contexts.get(name)
    
    def set_context(self, name: str, context: StorageContext):
        """设置指定名称的存储上下文"""
        self._storage_contexts[name] = context
        logger.info(f"已设置存储上下文: {name}")
    
    def has_context(self, name: str) -> bool:
        """检查是否存在指定名称的存储上下文"""
        return name in self._storage_contexts
    
    def clear_context(self, name: str):
        """清除指定名称的存储上下文"""
        if name in self._storage_contexts:
            del self._storage_contexts[name]
            logger.info(f"已清除存储上下文: {name}")
    
    def clear_all(self):
        """清除所有存储上下文"""
        self._storage_contexts.clear()
        logger.info("已清除所有存储上下文")

def ensure_storage_dir_exists():
    """确保存储目录存在"""
    os.makedirs(VECTOR_CACHE_DIR, exist_ok=True)
    os.makedirs(DOC_STORE_DIR, exist_ok=True)

def save_nodes_to_disk(nodes: List[BaseNode], store_name: str = "processed_nodes"):
    """将处理后的节点持久化到文档存储
    
    使用LlamaIndex的SimpleDocumentStore和StorageContext进行持久化，
    确保与LlamaIndex生态系统兼容性。
    
    Args:
        nodes: 要保存的节点列表
        store_name: 存储目录名称
        
    Returns:
        bool: 保存是否成功
    """
    ensure_storage_dir_exists()
    store_dir = os.path.join(DOC_STORE_DIR, store_name)
    
    try:
        # 创建文档存储
        doc_store = SimpleDocumentStore()
        doc_store.add_documents(nodes)
        
        # 创建存储上下文并持久化
        storage_context = StorageContext.from_defaults(docstore=doc_store)
        storage_context.persist(persist_dir=store_dir)
        
        # 存储到单例管理器
        context_manager = StorageContextManager.get_instance()
        context_manager.set_context(store_name, storage_context)
        context_manager.set_default_context(storage_context)
        
        logger.info(f"已将{len(nodes)}个节点保存至文档存储: {store_dir}")
        return True
    except Exception as e:
        logger.error(f"保存节点至文档存储时出错: {e}")
        return False
        
def load_nodes_from_disk(store_name: str = "processed_nodes") -> Optional[List[BaseNode]]:
    """从文档存储加载持久化的节点
    
    从LlamaIndex的SimpleDocumentStore加载节点。
    
    Args:
        store_name: 存储目录名称
        
    Returns:
        Optional[List[BaseNode]]: 加载的节点列表，如果加载失败则返回None
    """
    # 存储路径
    store_dir = os.path.join(DOC_STORE_DIR, store_name)
    
    # 检查存储是否存在
    if not os.path.exists(store_dir):
        logger.info(f"找不到文档存储: {store_dir}")
        return None
        
    try:
        # 从持久化存储加载
        storage_context = StorageContext.from_defaults(persist_dir=store_dir)
        doc_store = storage_context.docstore
        
        # 存储到单例管理器
        context_manager = StorageContextManager.get_instance()
        context_manager.set_context(store_name, storage_context)
        context_manager.set_default_context(storage_context)
        
        # 获取所有文档节点
        nodes = list(doc_store.docs.values())
        logger.info(f"已从文档存储 {store_dir} 加载 {len(nodes)} 个节点")
        return nodes
    except Exception as e:
        logger.error(f"从文档存储加载节点时出错: {e}")
        return None

def build_query_engine(docs: list[TextNode]) -> Dict:
    """
    构建文档查询引擎，带有缓存机制。
    根据文档类别（doc.metadata.category）对查询引擎进行分组。
    
    Args:
        docs: 文档列表
    
    Returns:
        Dict: 包含两个字典: 
            - 'by_id': 以文档ID为键的查询引擎字典
            - 'by_category': 以类别为键、文档ID列表为值的字典
    """
    ensure_storage_dir_exists()

    # 构建查询引擎字典 - 按ID索引
    engines_by_id = {}
    
    # 构建查询引擎字典 - 按类别分组
    engines_by_category = {}
    
    for idx, doc in enumerate(docs):
        all_nodes = []
        # 根据文档类型选择适当的解析器
        node_parser = get_parser_for_document(doc)
        
        # 使用选择的解析器处理文档
        nodes = node_parser.get_nodes_from_documents([doc])
        all_nodes.extend(nodes)
        
        # 缓存路径
        cache_path = f"./{VECTOR_CACHE_DIR}/{doc.id_}"
        
        # 检查是否有缓存
        if os.path.exists(cache_path):
            logger.info(f"从缓存加载文档 {doc.id_} 的向量索引")
            try:
                vector_index = load_index_from_storage(
                    StorageContext.from_defaults(
                        persist_dir=cache_path
                    )
                )
            except Exception as e:
                logger.warning(f"从缓存加载索引失败: {e}，将重建索引")
                vector_index = VectorStoreIndex(all_nodes)
                # 保存到缓存
                vector_index.storage_context.persist(persist_dir=cache_path)
        else:
            logger.info(f"为文档 {doc.id_} 创建新的向量索引并缓存")
            # 构建新的索引并缓存
            vector_index = VectorStoreIndex(all_nodes)
            # 保存到缓存
            vector_index.storage_context.persist(persist_dir=cache_path)

        # 创建查询引擎
        vector_query_engine = vector_index.as_query_engine()
        
        # 存储到ID映射
        engines_by_id[doc.id_] = vector_query_engine
        
        # 获取文档类别
        category = "未分类"
        if hasattr(doc, 'metadata') and 'category' in doc.metadata:
            category = doc.metadata['category']
        
        # 将文档ID添加到对应类别
        if category not in engines_by_category:
            engines_by_category[category] = []
        engines_by_category[category].append(doc.id_)

    return {
        "by_id": engines_by_id,   # 以文档ID为键的查询引擎字典
        "by_category": engines_by_category  # 以类别为键、文档ID列表为值的字典
    }

"""
 文档加载
"""
def build_tool_agents() -> Dict:
    """
    文档加载
    """
    logger.info("开始加载文档...")

    try:
        # 首先尝试从磁盘加载持久化的节点
        loaded_nodes = load_nodes_from_disk()
        
        # 如果找到了持久化的节点，直接使用
        if loaded_nodes is not None:
            logger.info("已加载持久化的节点数据")
            docs = loaded_nodes
        else:
            # 如果没有持久化节点，调用ingestion_pipeline处理文档
            docs = run_ingestion_pipeline()
            # 将处理后的节点持久化保存
            save_nodes_to_disk(docs)
            # 重新加载
            docs = load_nodes_from_disk()
            
        logger.info(f"文档加载成功，共 {len(docs)} 个节点")
        return build_document_agents(docs=docs)
    except Exception as e:
        logger.error(f"文档加载失败: {e}", exc_info=True)
        raise

def build_document_agents(docs: List[TextNode]) -> Dict:
    """
    将每个文档独立封装为查询引擎
    
    参数:
        docs: 文档节点列表
        
    返回:
        文档ID到查询引擎的映射字典
    """
    logger.info(f"开始构建文档查询引擎，共 {len(docs)} 个文档节点")
  
    doc_engine = build_query_engine(docs=docs)
    
    # 检查是否有查询引擎构建成功
    if not doc_engine["by_id"]:
        logger.warning("没有成功构建任何查询引擎，返回空结果")
        return {}

    doc_agents = build_category_agents(
        doc_agents=doc_engine["by_id"], 
        categories=doc_engine["by_category"]
    )

    return doc_agents


def build_category_agents(
    doc_agents: Dict, 
    categories: Dict[str, List[str]]
) -> Dict[str, ReActAgent]:
    """
    按照类别创建不同的Agent
    
    参数:
        doc_agents: 文档ID到查询引擎的映射字典
        categories: 类别到文档ID列表的映射字典
        
    返回:
        类别到Agent的映射字典
    """
    category_agents = {}
    
    for category, doc_ids in categories.items():
        # 筛选该类别下的文档代理
        category_doc_engines = {doc_id: doc_agents[doc_id] for doc_id in doc_ids if doc_id in doc_agents}
        
        if not category_doc_engines:
            logger.warning(f"类别 '{category}' 没有有效的文档引擎，跳过")
            continue
            
        try:
            # 为该类别创建专门的Agent
            category_agent = _build_agent_for_category(
                category=category,
                doc_agents=category_doc_engines
            )
            
            category_agents[category] = category_agent
        except Exception as e:
            logger.error(f"为类别 '{category}' 构建代理失败: {e}")
    
    return category_agents


def _build_agent_for_category(
    category: str,
    doc_agents: Dict
) -> ReActAgent:
    """
    为特定类别构建代理
    
    参数:
        category: 类别名称
        doc_agents: 该类别下的文档ID到查询引擎的映射字典
        
    返回:
        配置好的ReAct代理实例
    """
    logger.info(f"开始为类别 '{category}' 构建代理，共 {len(doc_agents)} 个文档")
    # 为每个文档代理创建对应的查询工具
    category_tools = []
    
    # 从单例管理器获取存储上下文
    context_manager = StorageContextManager.get_instance()
    storage_context = context_manager.get_default_context()
    
    # 获取文档存储
    doc_store = storage_context.docstore if storage_context else None
    
    for doc_id, query_engine in doc_agents.items():
        try:
            # 尝试从存储上下文中获取节点
            node = None
            if doc_store and doc_id in doc_store.docs:
                node = doc_store.get_document(doc_id)
                logger.info(f"从文档存储中获取到文档 {doc_id}")
              
            # 如果仍未找到，使用默认值
            if node is None:
                # 如果找不到对应节点，使用默认摘要
                summary = f"用于查询{category}类别中的文档{doc_id}"
                logger.warning(f"找不到文档 {doc_id} 的原始节点，使用默认摘要")
            else:
                # 确保metadata是字典类型
                if not isinstance(node.metadata, dict):
                    logger.warning(f"文档 {doc_id} 的metadata不是字典类型，使用默认摘要")
                    node.metadata = {}
                # 获取摘要，如果不存在则使用默认描述
                summary = node.metadata.get('summary', f"用于查询{category}类别中的文档{doc_id}")
                if 'summary' not in node.metadata:
                    logger.warning(f"文档 {doc_id} 没有摘要，使用默认描述")

            logger.info(f"文档 {doc_id} 的摘要: {summary}")
   
            # 创建查询引擎工具，将文档代理包装为工具
            doc_tool = QueryEngineTool(
                query_engine=query_engine,
                metadata=ToolMetadata(
                    name=f"{category}_{doc_id}",
                    description=summary,
                ),
            )
            category_tools.append(doc_tool)
        except Exception as e:
            logger.error(f"为文档 {doc_id} 创建查询工具失败: {e}")
    
    if not category_tools:
        logger.error(f"类别 '{category}' 没有成功创建任何查询工具，无法构建代理")
        raise ValueError(f"类别 '{category}' 没有有效的查询工具")
        
    logger.info(f"成功为类别 '{category}' 创建了 {len(category_tools)} 个查询工具")
    
    # 创建工具到节点的映射关系
    try:
        # 创建工具映射
        tool_mapping = SimpleToolNodeMapping.from_objects(category_tools)
        
        # 使用存储上下文(如果有)创建索引
        if storage_context:
            logger.info(f"使用存储上下文为类别 '{category}' 创建索引")
            obj_index = ObjectIndex.from_objects(
                objects=category_tools, 
                tool_node_mapping=tool_mapping, 
                index_cls=VectorStoreIndex,
                storage_context=storage_context
            )
        else:
            logger.info(f"为类别 '{category}' 创建新索引")
            obj_index = ObjectIndex.from_objects(
                objects=category_tools, 
                tool_node_mapping=tool_mapping, 
                index_cls=VectorStoreIndex
            )

        # 使用DeepSeek作为LLM   
        llm = LLMFactory.create_llm(LLMProviderType.QIANWENOPENAI)
        
        # 使用ReActAgent替代OpenAIAgent
        category_agent = ReActAgent.from_tools(
            tool_retriever=obj_index.as_retriever(similarity_top_k=7),
            llm=llm,
            verbose=True,
            system_prompt=f""" \
        您是一个回答关于{category}类别问题的代理。
        请始终使用提供的工具来回答问题。不要依赖先验知识。使用清晰详细的查询传递工具，然后充分利用它们的响应来回答原始查询。
        """
        )
        logger.info(f"类别 '{category}' 的代理创建成功")
        return category_agent
    except Exception as e:
        logger.error(f"创建类别 '{category}' 的代理失败: {e}", exc_info=True)
        raise

