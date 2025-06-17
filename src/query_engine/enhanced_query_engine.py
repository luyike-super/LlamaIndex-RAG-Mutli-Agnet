"""
增强的查询引擎，支持重排序、混合检索和查询优化
"""
from typing import List, Optional, Any, Dict
from llama_index.core import VectorStoreIndex
from llama_index.core.query_engine import BaseQueryEngine
from llama_index.core.schema import NodeWithScore, QueryBundle
from llama_index.core.response import Response
from llama_index.core.retrievers import BaseRetriever
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core.response_synthesizers import get_response_synthesizer
from llama_index.core.callbacks import CallbackManager
from config.config_rag import RETRIEVAL_CONFIG, QUERY_CONFIG
import logging

logger = logging.getLogger(__name__)

class EnhancedQueryEngine(BaseQueryEngine):
    """
    增强的查询引擎，支持：
    1. 重排序机制
    2. 相似度阈值过滤
    3. 查询优化
    4. 混合检索策略
    """
    
    def __init__(
        self,
        retriever: BaseRetriever,
        response_synthesizer: Optional[Any] = None,
        node_postprocessors: Optional[List[Any]] = None,
        enable_reranking: bool = True,
        similarity_cutoff: float = 0.7,
        rerank_top_k: int = 5,
        callback_manager: Optional[Any] = None,
    ):
        self._retriever = retriever
        
        # 确保response_synthesizer不为None
        if response_synthesizer is None:
            self._response_synthesizer = get_response_synthesizer()
        else:
            self._response_synthesizer = response_synthesizer
            
        self._node_postprocessors = node_postprocessors or []
        self._enable_reranking = enable_reranking
        self._similarity_cutoff = similarity_cutoff
        self._rerank_top_k = rerank_top_k
        
        # 确保callback_manager不为None
        if callback_manager is None:
            self.callback_manager = CallbackManager([])
        else:
            self.callback_manager = callback_manager
        
        # 添加相似度后处理器
        if similarity_cutoff > 0:
            similarity_processor = SimilarityPostprocessor(
                similarity_cutoff=similarity_cutoff
            )
            self._node_postprocessors.append(similarity_processor)
    
    def get_retrieved_nodes(self, query: str) -> List[NodeWithScore]:
        """
        专门用于获取检索到的节点，不生成文本响应
        
        Args:
            query: 查询字符串
            
        Returns:
            List[NodeWithScore]: 检索到的节点列表，包含分数
        """
        # 创建查询包
        query_bundle = QueryBundle(query_str=query)
        
        # 1. 查询优化
        optimized_query = self._optimize_query(query_bundle)
        
        # 2. 检索相关节点
        nodes_with_scores = self._retrieve_nodes(optimized_query)
        
        # 3. 后处理（包括重排序）
        processed_nodes = self._postprocess_nodes(
            nodes_with_scores, optimized_query
        )
        
        logger.info(f"最终返回 {len(processed_nodes)} 个检索节点")
        return processed_nodes
    
    def _query(self, query_bundle: QueryBundle) -> Response:
        """执行查询"""
        # 1. 查询优化
        optimized_query = self._optimize_query(query_bundle)
        
        # 2. 检索相关节点
        nodes_with_scores = self._retrieve_nodes(optimized_query)
        
        # 3. 后处理（包括重排序）
        processed_nodes = self._postprocess_nodes(
            nodes_with_scores, optimized_query
        )
        
        # 4. 生成响应，确保包含source_nodes
        if self._response_synthesizer:
            response = self._response_synthesizer.synthesize(
                query=optimized_query,
                nodes=processed_nodes
            )
            # 确保response有source_nodes
            if not hasattr(response, 'source_nodes') or not response.source_nodes:
                response.source_nodes = processed_nodes
        else:
            # 简单合并节点内容作为响应
            response_text = "\n\n".join([
                node.node.get_content() for node in processed_nodes[:3]
            ])
            response = Response(response=response_text, source_nodes=processed_nodes)
        
        logger.info(f"查询响应包含 {len(response.source_nodes)} 个源节点")
        return response
    
    async def _aquery(self, query_bundle: QueryBundle) -> Response:
        """异步查询方法"""
        # 对于这个实现，我们简单地调用同步版本
        return self._query(query_bundle)
    
    def _get_prompt_modules(self) -> Dict[str, Any]:
        """获取提示模块（抽象方法实现）"""
        # 返回空字典，因为我们不使用提示模块
        return {}
    
    def _optimize_query(self, query_bundle: QueryBundle) -> QueryBundle:
        """查询优化"""
        query_text = query_bundle.query_str
        
        # 查询扩展（如果启用）
        if QUERY_CONFIG.get("enable_query_expansion", False):
            query_text = self._expand_query(query_text)
        
        # 查询重写（如果启用）
        if QUERY_CONFIG.get("enable_query_rewrite", False):
            query_text = self._rewrite_query(query_text)
        
        return QueryBundle(
            query_str=query_text,
            embedding=query_bundle.embedding,
            custom_embedding_strs=query_bundle.custom_embedding_strs
        )
    
    def _expand_query(self, query: str) -> str:
        """查询扩展 - 添加同义词或相关术语"""
        # 简单的同义词映射示例
        synonyms_map = {
            "硬件控制": ["hardware control", "硬件管理", "设备控制"],
            "HCSL": ["High Speed Current Steering Logic", "高速电流导向逻辑"],
            "输出类型": ["output type", "输出模式", "输出格式"],
            "时钟": ["clock", "CLK", "时钟信号"],
            "芯片": ["chip", "IC", "集成电路"],
        }
        
        expanded_terms = []
        for term, synonyms in synonyms_map.items():
            if term in query:
                expanded_terms.extend(synonyms[:2])  # 只添加前2个同义词
        
        if expanded_terms:
            query += " " + " ".join(expanded_terms)
        
        return query
    
    def _rewrite_query(self, query: str) -> str:
        """查询重写 - 改善查询表达"""
        # 简单的查询规范化
        query = query.strip()
        
        # 限制查询长度
        max_length = QUERY_CONFIG.get("max_query_length", 200)
        if len(query) > max_length:
            query = query[:max_length].rsplit(' ', 1)[0]
        
        return query
    
    def _retrieve_nodes(self, query_bundle: QueryBundle) -> List[NodeWithScore]:
        """检索节点"""
        try:
            # 使用配置的top_k进行检索
            similarity_top_k = RETRIEVAL_CONFIG.get("similarity_top_k", 10)
            
            # 设置检索器的top_k
            if hasattr(self._retriever, '_similarity_top_k'):
                self._retriever._similarity_top_k = similarity_top_k
            
            nodes = self._retriever.retrieve(query_bundle)
            logger.info(f"检索到 {len(nodes)} 个相关节点")
            return nodes
        except Exception as e:
            logger.error(f"检索节点时出错: {e}")
            return []
    
    def _postprocess_nodes(
        self, 
        nodes: List[NodeWithScore], 
        query_bundle: QueryBundle
    ) -> List[NodeWithScore]:
        """后处理节点"""
        # 应用所有后处理器
        for processor in self._node_postprocessors:
            nodes = processor.postprocess_nodes(nodes, query_bundle)
        
        # 重排序（如果启用）
        if self._enable_reranking and RETRIEVAL_CONFIG.get("enable_reranking", False):
            nodes = self._rerank_nodes(nodes, query_bundle)
        
        # 限制返回数量
        rerank_top_k = RETRIEVAL_CONFIG.get("rerank_top_k", 5)
        nodes = nodes[:rerank_top_k]
        
        logger.info(f"后处理后保留 {len(nodes)} 个节点")
        return nodes
    
    def _rerank_nodes(
        self, 
        nodes: List[NodeWithScore], 
        query_bundle: QueryBundle
    ) -> List[NodeWithScore]:
        """重排序节点"""
        # 简单的基于关键词匹配的重排序
        query_lower = query_bundle.query_str.lower()
        query_keywords = set(query_lower.split())
        
        def calculate_keyword_score(node: NodeWithScore) -> float:
            """计算关键词匹配分数"""
            content_lower = node.node.get_content().lower()
            content_words = set(content_lower.split())
            
            # 计算关键词重叠度
            overlap = len(query_keywords.intersection(content_words))
            total_query_words = len(query_keywords)
            
            if total_query_words == 0:
                return 0.0
            
            keyword_score = overlap / total_query_words
            return keyword_score
        
        # 重新计算分数（结合原始相似度分数和关键词分数）
        for node in nodes:
            keyword_score = calculate_keyword_score(node)
            # 原始分数权重0.7，关键词分数权重0.3
            node.score = 0.7 * (node.score or 0) + 0.3 * keyword_score
        
        # 按新分数排序
        nodes.sort(key=lambda x: x.score or 0, reverse=True)
        
        return nodes

def create_enhanced_query_engine(
    index: VectorStoreIndex,
    **kwargs
) -> EnhancedQueryEngine:
    """
    创建增强的查询引擎
    
    Args:
        index: 向量索引
        **kwargs: 额外参数
        
    Returns:
        EnhancedQueryEngine: 增强的查询引擎实例
    """
    # 从配置获取参数
    config = RETRIEVAL_CONFIG
    
    # 创建检索器
    retriever = index.as_retriever(
        similarity_top_k=config.get("similarity_top_k", 10)
    )
    
    # 创建增强查询引擎
    query_engine = EnhancedQueryEngine(
        retriever=retriever,
        enable_reranking=config.get("enable_reranking", True),
        similarity_cutoff=config.get("similarity_cutoff", 0.7),
        rerank_top_k=config.get("rerank_top_k", 5),
        **kwargs
    )
    
    return query_engine 