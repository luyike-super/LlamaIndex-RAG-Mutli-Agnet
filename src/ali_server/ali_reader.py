import os

os.environ['DASHSCOPE_API_KEY'] = "<Your API Key>"
os.environ['DASHSCOPE_WORKSPACE_ID'] = "<Your Workspace id, Default workspace is empty.>"
"""
文档地址: 
https://help.aliyun.com/zh/model-studio/dashscopeparse?spm=a2c4g.11186623.help-menu-2400256.d_3_2_0_3.11c73889DHd1zy
"""
from llama_index.readers.dashscope.base import DashScopeParse
from llama_index.readers.dashscope.utils import ResultType

file = ['aiayn.pdf', 'not_exist.pdf']
parse = DashScopeParse(result_type=ResultType.DASHSCOPE_DOCMIND, category_id="<category id>")
documents = parse.load_data(file_path=file)