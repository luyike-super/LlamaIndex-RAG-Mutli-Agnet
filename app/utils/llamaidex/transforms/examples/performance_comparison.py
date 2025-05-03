"""
摘要生成性能对比示例

展示优化后的并发异步处理相比顺序处理的性能提升
"""

import logging
import asyncio
import time
from llama_index.core.schema import TextNode
from app.utils.llamaidex.transforms.summary import Summary

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 生成测试数据
def generate_test_data(count=20):
    """生成测试数据"""
    test_texts = [
        "人工智能(AI)是计算机科学的一个分支，它企图了解智能的实质，并生产出一种新的能以人类智能相似的方式做出反应的智能机器。",
        "大型语言模型（LLM）是一种基于深度学习和大数据训练的自然语言处理模型，能够理解和生成人类语言。",
        "RAG（检索增强生成）是结合检索系统和生成模型的混合架构，用于提高大模型回答的准确性。",
        "Python是一种广泛使用的解释型、高级编程语言，由Guido van Rossum于1991年创建。",
        "Docker是一个开源的应用容器引擎，基于Go语言并遵从Apache2.0协议开源。"
    ]
    
    nodes = []
    for i in range(count):
        text_index = i % len(test_texts)
        # 为每个文本添加一些变化，避免完全相同的内容
        text = f"{test_texts[text_index]} 示例#{i+1}"
        nodes.append(TextNode(text=text, metadata={"source": f"测试数据-{i+1}"}))
    
    return nodes

# 创建一个模拟顺序处理的组件
class SequentialSummary(Summary):
    """模拟顺序处理的摘要组件"""
    
    async def acall(self, nodes, **kwargs):
        """顺序处理节点"""
        try:
            summarizer = tree_summarize(
                llm=self.llm_model,
                summary_template=self.summary_prompt
            )
            
            processed_nodes = []
            
            logger.info(f"开始顺序处理 {len(nodes)} 个节点的摘要...")
            
            for node in nodes:
                # 获取节点文本内容
                text = node.get_content()
                
                # 生成摘要
                summary = await summarizer.aget_response(text)
                
                # 将摘要添加到节点的元数据中
                if isinstance(node, NodeWithScore):
                    node.node.metadata[self.summary_key] = summary
                else:
                    node.metadata[self.summary_key] = summary
                
                processed_nodes.append(node)
            
            logger.info(f"顺序处理完成，共处理 {len(processed_nodes)} 个节点")
            return processed_nodes
            
        except Exception as e:
            logger.error(f"顺序生成摘要时出错: {str(e)}")
            return nodes

async def run_performance_test():
    """运行性能测试"""
    # 生成测试数据
    node_count = 10  # 节点数量
    test_nodes = generate_test_data(node_count)
    
    # 创建顺序处理组件
    sequential_summary = SequentialSummary(
        summary_key="sequential_summary",
        summary_prompt="简单总结一下这段内容: {text}"
    )
    
    # 创建并发处理组件
    concurrent_summary = Summary(
        summary_key="concurrent_summary",
        summary_prompt="简单总结一下这段内容: {text}",
        max_concurrency=5,  # 限制并发数为5
        show_progress=True
    )
    
    # 运行顺序处理测试
    logger.info("=" * 50)
    logger.info("开始顺序处理测试...")
    start_time = time.time()
    await sequential_summary.acall(test_nodes.copy())
    sequential_time = time.time() - start_time
    logger.info(f"顺序处理耗时: {sequential_time:.2f} 秒")
    
    # 运行并发处理测试
    logger.info("=" * 50)
    logger.info("开始并发处理测试...")
    start_time = time.time()
    await concurrent_summary.acall(test_nodes.copy())
    concurrent_time = time.time() - start_time
    logger.info(f"并发处理耗时: {concurrent_time:.2f} 秒")
    
    # 性能对比
    speedup = sequential_time / concurrent_time if concurrent_time > 0 else float('inf')
    logger.info("=" * 50)
    logger.info(f"性能对比:")
    logger.info(f"- 顺序处理: {sequential_time:.2f} 秒")
    logger.info(f"- 并发处理: {concurrent_time:.2f} 秒")
    logger.info(f"- 加速比: {speedup:.2f}x")
    logger.info(f"- 性能提升: {(speedup-1)*100:.1f}%")
    
if __name__ == "__main__":
    # 导入必要的模块
    from llama_index.core.schema import NodeWithScore
    from llama_index.core.response_synthesizers import tree_summarize
    
    # 运行性能测试
    asyncio.run(run_performance_test()) 