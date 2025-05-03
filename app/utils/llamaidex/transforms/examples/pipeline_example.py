"""
处理流水线示例 - 展示如何在文档处理流水线中使用Summary组件
"""

import logging
from llama_index.core.schema import TextNode
from llama_index.core.node_parser import SimpleNodeParser
from llama_index.core.ingestion import IngestionPipeline
from app.utils.llamaidex.transforms.summary import Summary

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_pipeline_example():
    """运行包含摘要组件的处理流水线示例"""
    
    # 创建一个简单的文档内容
    sample_documents = [
        "大语言模型（Large Language Models，简称LLM）是基于深度学习技术开发的先进自然语言处理系统，能够理解和生成人类语言。这些模型通过分析海量文本数据学习语言规律和知识，具备强大的文本生成、理解和转换能力。LLM的应用范围极广，从智能对话助手、自动内容创作到辅助编程和知识管理等诸多领域。",
        "检索增强生成（Retrieval-Augmented Generation，简称RAG）是一种将检索系统与生成模型结合的混合架构。这种技术首先从外部知识库中检索与用户查询相关的信息，然后将这些信息与原始查询一起提供给大语言模型，指导模型生成更准确、更有依据的回答。RAG技术有效解决了大语言模型的幻觉问题，提高了生成内容的可靠性和时效性。"
    ]
    
    # 创建节点解析器 - 将文档分割成更小的节点
    node_parser = SimpleNodeParser.from_defaults()
    
    # 创建摘要组件
    summary_transform = Summary(
        summary_key="summary",
        summary_prompt="请用2-3句话概括以下内容的要点：{text}"
    )
    
    # 创建处理流水线
    pipeline = IngestionPipeline(
        transformations=[
            node_parser,  # 第一步：将文档解析为节点
            summary_transform,  # 第二步：为每个节点生成摘要
        ]
    )
    
    # 运行流水线处理文档
    logger.info("开始处理文档流水线...")
    nodes = pipeline.run(documents=sample_documents)
    
    # 显示处理结果
    logger.info(f"处理完成，共生成 {len(nodes)} 个节点")
    
    for i, node in enumerate(nodes):
        logger.info(f"节点 {i+1}:")
        logger.info(f"内容: {node.get_content()[:100]}...")
        logger.info(f"摘要: {node.metadata.get('summary')}")
        logger.info("-" * 60)
    
    return nodes

# 在实际应用中的使用示例：创建索引时添加摘要
def index_with_summary_example():
    """在创建索引时添加摘要示例（伪代码）"""
    
    # 伪代码 - 展示在实际应用中如何使用
    """
    from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
    from llama_index.core.ingestion import IngestionPipeline
    
    # 1. 加载文档
    documents = SimpleDirectoryReader("./data").load_data()
    
    # 2. 创建包含摘要组件的处理流水线
    pipeline = IngestionPipeline(
        transformations=[
            SimpleNodeParser.from_defaults(),
            Summary(summary_key="document_summary")
        ]
    )
    
    # 3. 处理文档并创建索引
    nodes = pipeline.run(documents)
    index = VectorStoreIndex(nodes)
    
    # 4. 查询时可以使用摘要
    query_engine = index.as_query_engine()
    response = query_engine.query("关于大语言模型的最新进展?")
    
    # 5. 显示查询结果及其来源的摘要
    print(f"回答: {response.response}")
    for source_node in response.source_nodes:
        print(f"来源摘要: {source_node.node.metadata.get('document_summary')}")
    """

if __name__ == "__main__":
    run_pipeline_example()
    # 实际应用示例仅为伪代码展示，不会执行 