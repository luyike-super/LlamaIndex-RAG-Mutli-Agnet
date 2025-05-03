from llama_index.readers.file import FlatReader, DocxReader, MarkdownReader
from llama_index.core.readers import SimpleDirectoryReader
from typing import Dict, Any, List, Optional
from llama_index.core.schema import Document

# 导入配置
from config.config_rag import DOCUMENT_CONFIG


class DocumentReader:
    """文档读取器，用于从目录中加载文档"""
    
    def __init__(
        self,
        input_dir: str = DOCUMENT_CONFIG["input_dir"],
        recursive: bool = DOCUMENT_CONFIG["recursive"] | True,
        file_extractor: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """
        初始化文档读取器
        
        Args:
            input_dir: 文档目录路径
            recursive: 是否递归读取子目录
            file_extractor: 文件类型与对应提取器的映射
            **kwargs: 传递给SimpleDirectoryReader的其他参数
        """
        if file_extractor is None:
            file_extractor = {}
            # 从配置中读取支持的文件类型
            for ext in DOCUMENT_CONFIG["supported_file_types"]:
                if ext in [".md", ".mdx"]:
                    file_extractor[ext] = FlatReader()
                elif ext == ".docx":
                    file_extractor[ext] = DocxReader()
            
        self.reader_config = {
            "input_dir": input_dir,
            "recursive": recursive,
            "file_extractor": file_extractor,
            **kwargs
        }
        
        self.reader = SimpleDirectoryReader(**self.reader_config)
    
    def load_data(self) -> List[Document]:
        """加载文档数据"""
        return self.reader.load_data()
    
    def get_reader(self) -> SimpleDirectoryReader:
        """获取原始reader对象"""
        return self.reader


# 默认reader实例
default_reader = DocumentReader() 

