from llama_index.readers.file import FlatReader, DocxReader
from llama_index.core.readers import SimpleDirectoryReader
from typing import Dict, Any, List, Optional
from llama_index.core.schema import Document
from pathlib import Path

# 导入配置
from config.config_rag import DOCUMENT_CONFIG

# 自定义FlatReader实现，修复file参数问题
class CustomFlatReader(FlatReader):
    def load_data(self, path, extra_info=None):
        # 确保传递Path对象而不是字符串
        return super().load_data(file=Path(path), extra_info=extra_info)

# 自定义DocxReader实现
class CustomDocxReader(DocxReader):
    def load_data(self, path, extra_info=None):
        # 确保传递Path对象而不是字符串
        return super().load_data(file=Path(path), extra_info=extra_info)

# 默认reader实例
default_reader = SimpleDirectoryReader(input_dir=DOCUMENT_CONFIG["input_dir"], 
                                       recursive=True, 
                                       exclude=[".pdf"],
                                       file_extractor={
                                              ".md": CustomFlatReader(),
                                              ".mdx": CustomFlatReader(),
                                              ".docx": CustomDocxReader(), 
                                        }).load_data()


