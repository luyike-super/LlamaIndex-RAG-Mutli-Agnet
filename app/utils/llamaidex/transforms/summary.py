from llama_index.core.schema import TransformComponent, NodeWithScore
from llama_index.core.response_synthesizers import tree_summarize
from llama_index.core.prompts import BasePromptTemplate
from app.llm.create_llm import client_deepseek
import logging
import asyncio
from typing import List, Any, Optional

# 配置日志
logger = logging.getLogger(__name__)

# 文档摘要类
class Summary(TransformComponent):
    """
    文档摘要组件 - 为每个节点生成摘要并添加到节点的元数据中
    
    采用纯异步方式处理，nodes遍历和摘要生成被拆分为独立协程
    """
    
    def __init__(
        self,
        summary_key: str = "summary",
        llm_model = None,
        summary_prompt: str = "请对以下内容进行总结：{text}"
    ):
        """
        初始化摘要组件
        
        Args:
            summary_key (str): 存储摘要的元数据键名
            llm_model: 使用的LLM模型，默认使用client_deepseek
            summary_prompt (str): 摘要生成的提示模板
        """
        self.summary_key = summary_key
        self.llm_model = llm_model or client_deepseek
        self.summary_prompt = BasePromptTemplate.from_template(summary_prompt)
    
    def __call__(self, nodes, **kwargs):
        """
        为每个节点生成摘要并存储在元数据中 (同步入口)
        
        Args:
            nodes: 节点列表
            
        Returns:
            处理后的节点列表
        """
        # 对于同步调用，使用asyncio运行异步方法
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self.acall(nodes, **kwargs))
    
    async def _generate_summary(self, text, summarizer):
        """
        独立协程：生成文本摘要
        
        Args:
            text: 需要生成摘要的文本
            summarizer: 摘要生成器
            
        Returns:
            摘要文本
        """
        try:
            # 异步生成摘要
            summary = await summarizer.aget_response(text)
            return summary
        except Exception as e:
            logger.error(f"生成摘要时出错: {str(e)}")
            return f"摘要生成失败: {str(e)}"
    
    async def _process_node(self, node, summarizer):
        """
        独立协程：处理单个节点
        
        Args:
            node: 需要处理的节点
            summarizer: 摘要生成器
            
        Returns:
            处理后的节点
        """
        try:
            # 获取节点文本内容
            text = node.get_content()
            
            # 调用独立的摘要生成协程
            summary = await self._generate_summary(text, summarizer)
            
            # 将摘要添加到节点的元数据中
            if isinstance(node, NodeWithScore):
                node.node.metadata[self.summary_key] = summary
            else:
                node.metadata[self.summary_key] = summary
            
            logger.info(f"已为节点 {node.id_} 生成摘要")
            return node
        except Exception as e:
            logger.error(f"处理节点 {node.id_} 时出错: {str(e)}")
            return node
    
    async def acall(self, nodes, **kwargs):
        """
        异步顺序处理所有节点，为每个节点生成摘要并存储在元数据中
        
        Args:
            nodes: 节点列表
            
        Returns:
            处理后的节点列表
        """
        if not nodes:
            return []
            
        try:
            # 创建摘要生成器
            summarizer = tree_summarize(
                llm=self.llm_model,
                summary_template=self.summary_prompt
            )
            
            # 使用列表存储处理后的节点
            processed_nodes = []
            
            logger.info(f"开始顺序处理 {len(nodes)} 个节点的摘要...")
            
            # 顺序处理节点（不并发），但保持异步特性
            for i, node in enumerate(nodes):
                logger.debug(f"处理第 {i+1}/{len(nodes)} 个节点")
                # 调用独立的节点处理协程
                processed_node = await self._process_node(node, summarizer)
                processed_nodes.append(processed_node)
            
            logger.info(f"摘要生成完成，共处理 {len(processed_nodes)} 个节点")
            return processed_nodes
            
        except Exception as e:
            logger.error(f"处理摘要时出错: {str(e)}")
            # 发生错误时返回原始节点
            return nodes
