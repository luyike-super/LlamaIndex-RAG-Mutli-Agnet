import os
from config.config_models import LLMConfig
os.environ['DASHSCOPE_API_KEY'] = LLMConfig.DASHSCOPE_API_KEY
os.environ['DASHSCOPE_WORKSPACE_ID'] = LLMConfig.DASHSCOPE_WORKSPACE_ID
"""
文档地址: 
https://help.aliyun.com/zh/model-studio/dashscopeparse?spm=a2c4g.11186623.help-menu-2400256.d_3_2_0_3.11c73889DHd1zy
"""
from llama_index.readers.dashscope.base import DashScopeParse
from llama_index.readers.dashscope.utils import ResultType

file = ['data/手机的区别.pdf']
parse = DashScopeParse(result_type=ResultType.DASHSCOPE_DOCMIND, category_id=LLMConfig.DASHSCOPE_WORKSPACE_ID)

# list <llama_index.core.schema.Document >  
documents = parse.load_data(file_path=file)
print(documents)
