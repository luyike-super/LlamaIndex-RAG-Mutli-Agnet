import os
from llama_index.indices.managed.dashscope.retriever import DashScopeCloudRetriever

"""
DashScopeCloudRetriever是百炼提供的检索增强服务管理SDK。使用该工具可以便捷地通过LlamaIndex框架初始化LlamaIndex检索器。
"""
os.environ["DASHSCOPE_API_KEY"] = "your_api_key_here"
os.environ["DASHSCOPE_WORKSPACE_ID"] = "your_workspace_here"

retriever = DashScopeCloudRetriever("your index name")
nodes = retriever.retrieve("test query")
print(nodes)