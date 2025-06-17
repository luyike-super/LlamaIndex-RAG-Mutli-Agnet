"""
RAG 系统配置文件
"""

# 文档配置
DOCUMENT_CONFIG = {
    # 文档目录路径
    "input_dir": "data",
    
    # 是否递归读取子目录
    "recursive": True,
    
    # 支持的文件类型
    "supported_file_types": [".md", ".mdx", ".docx"],
}

# 检索配置
RETRIEVAL_CONFIG = {
    # 相似度检索参数
    "similarity_top_k": 15,  # 增加到15提高召回率
    "similarity_cutoff": 0.3,  # 大幅降低阈值以包含更多候选结果
    
    # 重排序配置
    "enable_reranking": True,
    "rerank_top_k": 8,  # 增加重排序保留数量
    
    # 混合检索配置
    "enable_hybrid_search": True,
    "alpha": 0.6,  # 调整向量检索权重，增加关键词匹配权重
}

# 文档分块配置
CHUNKING_CONFIG = {
    # Markdown文档
    "markdown": {
        "chunk_size": 800,
        "chunk_overlap": 100,
        "separator": "\n\n",
    },
    
    # Word文档
    "docx": {
        "chunk_size": 1200,
        "chunk_overlap": 150,
        "separator": "\n",
    },
    
    # JSON文档
    "json": {
        "chunk_size": 600,
        "chunk_overlap": 50,
        "separator": ",",
    },
    
    # 默认配置
    "default": {
        "chunk_size": 1024,
        "chunk_overlap": 200,
        "separator": " ",
    }
}

# Embedding配置
EMBEDDING_CONFIG = {
    "model_name": "text-embedding-v2",
    "batch_size": 100,
    "dimensions": 1536,
    "normalize_embeddings": True,
}

# 查询优化配置
QUERY_CONFIG = {
    # 查询扩展
    "enable_query_expansion": True,
    "expansion_method": "synonym",  # synonym, llm_expansion
    
    # 查询重写
    "enable_query_rewrite": True,
    "max_query_length": 200,
    
    # 多查询策略
    "enable_multi_query": True,
    "num_queries": 3,
}
