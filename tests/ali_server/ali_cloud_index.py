import os
from llama_index.readers.dashscope import DashScopeParse
from llama_index.indices.managed.dashscope import DashScopeCloudIndex

# 您可以通过 使用以下命令设置DASHSCOPE_WORKSPACE_ID（业务空间ID）的临时环境变量。
# os.environ["DASHSCOPE_WORKSPACE_ID"] = "llm-xxx<请替换为您的workspace_id>"
if "DASHSCOPE_WORKSPACE_ID" not in os.environ or os.environ["DASHSCOPE_WORKSPACE_ID"] is None:
    raise ValueError("DASHSCOPE_WORKSPACE_ID 未设置，无法操作 DashScope Cloud Index。")

# 设置需要上传的文件列表
file_list = [
    "./docs/阿里云百炼系列平板电脑产品介绍.pdf",
    "./docs/阿里云百炼系列手机产品介绍.docx",
    "./docs/阿里云百炼系列智能音箱产品介绍.txt"
]
# 上传文件并在云端进行智能化解析
documents = DashScopeParse(
    category="cate_xxx<请替换为数据类目 ID，不设置将使用默认类目>",
    # 支持更多参数设置
).load_data(file_path=file_list)
print("完成文档上传和智能化解析")

# 在云端进行智能切分并进行智能索引
index = DashScopeCloudIndex.from_documents(
    documents,
    name="my_first_index",
    # 支持更多参数设置
)
# 云端支持库支持以下操作
# 增加更多文档
# index._insert(documents)
# 删除部分文档
# index.delete_ref_doc([documents.doc_id])
print("完成云端知识库构建")

# 初始化检索引擎，retriever为DashScopeCloudRetriever类
retriever = index.as_retriever(
    # 支持更多参数设置
    # dense_similarity_top_k = 100,
    # sparse_similarity_top_k = 100,
    # enable_reranking = True,
    # ...
)
print("===========================================================================================================")
# 执行向量数据库检索
nodes = retriever.retrieve("你知道的阿里云百炼手机是什么吗？")
# 展示检索到的的第一个TextNode向量
print(nodes[0])