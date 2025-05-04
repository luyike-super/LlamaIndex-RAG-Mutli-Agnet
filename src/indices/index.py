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
import os

Settings.llm = LLMFactory.create_llm(LLMProviderType.OPENAI)
Settings.embed_model = EmbeddingFactory.create_embedding(EmbeddingProviderType.DASHSCOPE)


"""
 文档加载
"""
def test_load_docs() -> List[TextNode]:
   return build_document_agents(docs=run_ingestion_pipeline())


def build_document_agents(docs: List[TextNode]) -> Dict:
    """
    将每个文档独立封装为查询引擎
    
    参数:
        docs: 文档节点列表
        
    返回:
        文档ID到查询引擎的映射字典
    """
    doc_agents = {}
    for doc in docs:
        # 为每个文档创建独立的查询引擎
        doc_index = VectorStoreIndex([doc])
        doc_engine = doc_index.as_query_engine()
        doc_agents[doc.id_] = doc_engine
        
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
    # 为每个文档代理创建对应的查询工具
    category_tools = []
    for doc_id, query_engine in doc_agents.items():
        # 创建查询引擎工具，将文档代理包装为工具
        doc_tool = QueryEngineTool(
            query_engine=query_engine,
            metadata=ToolMetadata(
                name=f"{category}_{doc_id}",
                description=f"用于查询{category}类别中的文档{doc_id}",
            ),
        )
        category_tools.append(doc_tool)
    
   
    llm = LLMFactory.create_llm(LLMProviderType.DEEPSEEK)
    
    # 使用ReActAgent替代OpenAIAgent
    category_agent = ReActAgent.from_tools(
        tools=category_tools,
        llm=llm,
        verbose=True,
        system_prompt=f""" \
    您是一个专门回答关于LlamaIndex中{category}类别问题的代理。
    请始终使用提供的工具来回答问题。不要依赖先验知识。使用清晰详细的查询传递工具，然后充分利用它们的响应来回答原始查询。
    """
    )

    return category_agent

