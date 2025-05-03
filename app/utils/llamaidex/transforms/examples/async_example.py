"""
纯异步摘要生成示例

展示使用纯异步方式（非并发）处理节点和生成摘要
"""

import logging
import asyncio
import time
from llama_index.core.schema import TextNode, NodeWithScore
from llama_index.core.response_synthesizers import tree_summarize
from app.utils.llamaidex.transforms.summary import Summary

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_async_example():
    """运行纯异步示例"""
    
    # 创建测试节点
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
        summary_key="async_summary",
        summary_prompt="请用一句话概括以下内容：{text}"
    )
    
    # 异步处理节点
    logger.info("开始使用纯异步方式处理节点...")
    start_time = time.time()
    processed_nodes = await summary_transform.acall(nodes)
    end_time = time.time()
    
    # 显示结果
    logger.info(f"处理完成，耗时: {end_time - start_time:.2f}秒")
    for i, node in enumerate(processed_nodes):
        logger.info(f"节点 {i+1} 摘要: {node.metadata.get('async_summary')}")
        logger.info("-" * 50)
    
    return processed_nodes

# 自定义摘要组件使用示例
async def custom_summary_flow():
    """展示如何在自定义流程中使用拆分的协程"""
    
    # 创建测试节点
    node = TextNode(
        text="云计算是一种基于互联网的计算方式，通过这种方式，共享的软硬件资源和信息可以按需求提供给计算机各种终端和其他设备。云计算描述了一种基于互联网的新的IT服务增加、使用和交付模式，通常涉及通过互联网来提供动态易扩展且经常是虚拟化的资源。",
        metadata={"source": "云计算介绍", "type": "technology"}
    )
    
    # 创建摘要生成器
    from app.llm.create_llm import client_deepseek
    summarizer = tree_summarize(
        llm=client_deepseek,
        summary_template=BasePromptTemplate.from_template("请简要概括这段内容：{text}")
    )
    
    # 直接使用独立的摘要生成协程
    logger.info("开始自定义摘要流程...")
    
    # 创建Summary实例来访问内部方法
    summary_helper = Summary()
    
    # 获取文本内容
    text = node.get_content()
    
    # 使用独立的摘要生成协程
    summary = await summary_helper._generate_summary(text, summarizer)
    
    # 使用摘要结果
    logger.info(f"生成摘要: {summary}")
    
    # 可以将摘要添加到节点元数据或用于其他处理
    node.metadata["custom_summary"] = summary
    
    return node

if __name__ == "__main__":
    # 导入必要的模块
    from llama_index.core.prompts import BasePromptTemplate
    
    # 运行异步示例
    asyncio.run(run_async_example())
    
    # 运行自定义流程示例
    asyncio.run(custom_summary_flow()) 