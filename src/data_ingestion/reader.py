from llama_index.readers.file import FlatReader, DocxReader
from llama_index.core.readers import SimpleDirectoryReader
from typing import Dict, Any, List, Optional
from llama_index.core.schema import Document

# 导入配置
from config.config_rag import DOCUMENT_CONFIG


# 默认reader实例
default_reader = SimpleDirectoryReader(input_dir=DOCUMENT_CONFIG.DATA_DIR, 
                                       recursive=True, 
                                       required_exts=[".pdf", ".docx", ".md"],
                                       file_extractor={
                                              ".md":FlatReader,
                                              ".mdx":FlatReader,
                                              ".docx":DocxReader, 
                                        }) 

