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
