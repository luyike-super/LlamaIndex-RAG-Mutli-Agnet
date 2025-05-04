import sys
import os
import asyncio
import warnings

# 忽略特定的 asyncio 警告
warnings.filterwarnings("ignore", message="There is no current event loop")

# 添加项目根目录到路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from llama_index.core.schema import TextNode
from src.transformations.docs_summarizer_transform import DocsSummarizerTransform

async def demo_summarizer():
    """演示DocsSummarizerTransform的摘要功能"""
    # 创建转换器实例
    transform = DocsSummarizerTransform()
    
    # 创建测试节点
    sample_text = """
    LlamaIndex 是一个为LLM应用提供的数据框架，它使用结构化和非结构化数据提供以下功能:
    1. 数据摄取：从不同的数据源和格式摄取数据
    2. 数据索引：结构化数据，以便LLM可以有效地使用
    3. 数据检索：提供多种检索方法，从简单的向量检索到更复杂的路由器检索和混合检索
    4. 查询引擎：能够直接基于数据执行复杂的逻辑
    5. 代理工具：提供工具帮助LLM与其他API交互，打开可能性
    6. 应用集成：简单的接口和基于API的功能，便于与不同的应用集成
    
    LlamaIndex通过使用LLM的内在能力和专门的知识结构，帮助构建强大的知识工作应用。它使数据成为LLM交互的基础，确保回答基于事实，并减少幻觉问题。
    """
    
    test_node = TextNode(
        text=sample_text,
        id_="sample_doc"
    )
    nodes = [test_node]
    
    # 执行摘要转换
    print("开始摘要处理...")
    updated_nodes = await transform.acall(nodes)
    
    # 显示摘要结果
    print("\n===== 原始文本 =====")
    print(test_node.text)
    
    print("\n===== 生成的摘要 =====")
    print(test_node.metadata.get('summary'))

def run_demo():
    """运行演示，并处理事件循环清理"""
    # Windows平台下避免事件循环关闭错误的特殊处理
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    # 运行异步函数
    asyncio.run(demo_summarizer())
    
    # 确保所有任务都已完成并关闭
    # 防止在Windows上出现"RuntimeError: Event loop is closed"
    if sys.platform.startswith('win'):
        asyncio.get_event_loop().close()

if __name__ == "__main__":
    run_demo() 