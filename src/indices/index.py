from llama_index.core.settings import Settings
from llama_index.core.schema import TextNode
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.objects import ObjectIndex
from llama_index.core.storage import StorageContext
from llama_index.core.indices import VectorStoreIndex
from llama_index.core.indices.loading import load_index_from_storage
from llama_index.core.agent import ReActAgent
from src.models import LLMFactory, EmbeddingFactory, LLMProviderType, EmbeddingProviderType
from src.data_ingestion.ingestion_pipeline import run_ingestion_pipeline
from typing import List, Dict, Optional
from llama_index.core.objects.tool_node_mapping import SimpleToolNodeMapping
import os
import logging

# 配置基本日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('llama_kb.indices')

Settings.llm = LLMFactory.create_llm(LLMProviderType.QIANWENOPENAI)
Settings.embed_model = EmbeddingFactory.create_embedding(EmbeddingProviderType.DASHSCOPE)


"""
 文档加载
"""
def test_load_docs() -> Dict:
   logger.info("开始加载文档...")
   try:
       docs = run_ingestion_pipeline()
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
    doc_agents = {}
    for i, doc in enumerate(docs):
        # 为每个文档创建独立的查询引擎
        try:
            logger.debug(f"处理第 {i+1}/{len(docs)} 个文档 (ID: {doc.id_})")
            doc_index = VectorStoreIndex([doc])
            doc_engine = doc_index.as_query_engine()
            doc_agents[doc.id_] = doc_engine
        except Exception as e:
            logger.error(f"为文档 {doc.id_} 创建查询引擎失败: {e}")
            # 继续处理其他文档，不中断整个流程
    
    logger.info(f"文档查询引擎构建完成，共 {len(doc_agents)} 个")
    return doc_agents


def build_category_agents(doc_agents: Dict, categories: Dict[str, List[str]]) -> Dict[str, ReActAgent]:
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
        category_doc_agents = {doc_id: doc_agents[doc_id] for doc_id in doc_ids if doc_id in doc_agents}
        
        # 为该类别创建专门的Agent
        category_agent = _build_agent_for_category(
            category=category,
            doc_agents=category_doc_agents
        )
        
        category_agents[category] = category_agent
        
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
    for doc_id, query_engine in doc_agents.items():
        try:
            # 获取查询引擎中的节点
            node = query_engine._index.docstore.get_node(doc_id)
            # 获取摘要，如果不存在则使用默认描述
            summary = node.metadata.get('summary', f"用于查询{category}类别中的文档{doc_id}")

            logger.info(f"文档 {doc_id} 的摘要: {summary}")
            if 'summary' not in node.metadata:
                logger.warning(f"文档 {doc_id} 没有摘要，使用默认描述")
   
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
            docs_summarizer_transform.py .error(f"为文档 {doc_id} 创建查询工具失败: {e}")
    
    logger.info(f"成功为类别 '{category}' 创建了 {len(category_tools)} 个查询工具")
    
    # 创建工具到节点的映射关系
    try:
        tool_mapping = SimpleToolNodeMapping.from_objects(category_tools)

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

