"""
Summary组件使用示例

此示例展示如何使用Summary组件为节点添加摘要元数据
"""

import logging
from llama_index.core.schema import TextNode
from app.utils.llamaidex.transforms.summary import Summary

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_summary_example():
    """运行摘要示例"""
    
    # 创建一些测试节点
    nodes = [
        TextNode(
            text="人工智能(AI)是计算机科学的一个分支，它企图了解智能的实质，并生产出一种新的能以人类智能相似的方式做出反应的智能机器。人工智能是研究、开发用于模拟、延伸和扩展人的智能的理论、方法、技术及应用系统的一门新的技术科学。人工智能的研究包括机器人、语言识别、图像识别、自然语言处理和专家系统等。",
            metadata={"source": "AI基础知识", "type": "definition"}
        ),
        TextNode(
            text="大型语言模型（LLM）是一种基于深度学习和大数据训练的自然语言处理模型，能够理解和生成人类语言。LLM通过预训练和微调两个阶段学习语言规律和知识，具有上下文理解、生成连贯文本、多语言支持和知识表示等特点。代表性模型包括GPT、LLaMA、Claude等。LLM在智能助手、内容生成、教育辅助和知识提取等领域有广泛应用。",
            metadata={"source": "LLM概述", "type": "introduction"}
        ),
        TextNode(
            text="RAG（检索增强生成）是结合检索系统和生成模型的混合架构。检索增强生成首先从知识库中检索相关信息，然后将这些信息与用户的查询一起提供给大型语言模型，使模型能够基于检索到的上下文生成回答。这种方法结合了检索系统的信息获取能力和生成模型的文本创作能力，可以提高回答的准确性和可靠性，特别是对于需要特定领域知识或最新信息的查询。",
            metadata={"source": "RAG技术", "type": "technology"}
        )
    ]
    
    # 初始化摘要组件
    summary_transform = Summary(
        summary_key="brief_summary",  # 自定义摘要存储的键名
        summary_prompt="请用一句话概括以下内容：{text}"  # 自定义摘要提示
    )
    
    # 处理节点
    logger.info("开始为节点生成摘要...")
    processed_nodes = summary_transform(nodes)
    
    # 显示结果
    for i, node in enumerate(processed_nodes):
        logger.info(f"节点 {i+1} 原文: {node.get_content()[:50]}...")
        logger.info(f"节点 {i+1} 摘要: {node.metadata.get('brief_summary')}")
        logger.info("-" * 50)
    
    return processed_nodes

# 异步示例
async def run_async_summary_example():
    """运行异步摘要示例"""
    
    # 创建一些测试节点
    nodes = [
        TextNode(
            text="Python是一种广泛使用的解释型、高级编程语言，由Guido van Rossum于1991年创建。Python的设计强调代码的可读性和简洁的语法，这使得程序员能够用更少的代码表达概念。Python支持多种编程范式，包括面向对象、命令式、函数式和过程式编程。",
            metadata={"source": "Python介绍", "type": "programming"}
        ),
        TextNode(
            text="Docker是一个开源的应用容器引擎，基于Go语言并遵从Apache2.0协议开源。Docker可以让开发者打包他们的应用以及依赖包到一个轻量级、可移植的容器中，然后发布到任何流行的Linux机器上，也可以实现虚拟化。容器是完全使用沙箱机制，相互之间不会有任何接口。",
            metadata={"source": "Docker技术", "type": "technology"}
        )
    ]
    
    # 初始化摘要组件
    summary_transform = Summary()
    
    # 异步处理节点
    logger.info("开始异步为节点生成摘要...")
    processed_nodes = await summary_transform.acall(nodes)
    
    # 显示结果
    for i, node in enumerate(processed_nodes):
        logger.info(f"节点 {i+1} 原文: {node.get_content()[:50]}...")
        logger.info(f"节点 {i+1} 摘要: {node.metadata.get('summary')}")
        logger.info("-" * 50)
    
    return processed_nodes

if __name__ == "__main__":
    # 运行同步示例
    run_summary_example()
    
    # 运行异步示例
    import asyncio
    asyncio.run(run_async_summary_example()) 