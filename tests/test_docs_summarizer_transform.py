import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
import unittest
from unittest.mock import MagicMock, patch

from llama_index.core.schema import TextNode
from src.transformations.docs_summarizer_transform import DocsSummarizerTransform
from src.models import LLMFactory, LLMProviderType

class TestDocsSummarizerTransform(unittest.TestCase):
    """测试 DocsSummarizerTransform 类"""

    def setUp(self):
        """测试前的准备工作"""
        self.transform = DocsSummarizerTransform()
        
        # 创建测试节点
        self.test_node = TextNode(
            text="这是一个测试文档页面，用于测试摘要功能。"*10,
            id_="test_node_1"
        )
        self.nodes = [self.test_node]

    def test_call(self):
        """测试同步调用方法"""
        result = self.transform(self.nodes)
        self.assertEqual(result, self.nodes)

    @patch('src.transformations.docs_summarizer_transform.TreeSummarize')
    @patch('src.models.LLMFactory.create_llm')
    def test_acall(self, mock_create_llm, mock_tree_summarize):
        """测试异步调用方法"""
        # 使用同步测试运行异步方法
        async def run_test():
            # 模拟LLM和TreeSummarize
            mock_llm = MagicMock()
            mock_create_llm.return_value = mock_llm
            
            mock_summarizer = MagicMock()
            # 确保aget_response返回一个协程对象
            mock_summarizer.aget_response = MagicMock(return_value=asyncio.Future())
            mock_summarizer.aget_response.return_value.set_result("这是一个测试摘要。")
            mock_tree_summarize.return_value = mock_summarizer
            
            # 执行测试
            result = await self.transform.acall(self.nodes)
            
            # 验证结果
            self.assertEqual(result, self.nodes)
            mock_summarizer.aget_response.assert_called()
        
        # 运行异步测试
        asyncio.run(run_test())

    def test_process_nodes(self):
        """测试处理节点的方法"""
        async def test_process():
            mock_summarizer = MagicMock()
            # 确保aget_response返回一个协程对象
            future = asyncio.Future()
            future.set_result("这是一个测试摘要。")
            mock_summarizer.aget_response = MagicMock(return_value=future)
            prompt = "测试提示"
            
            await self.transform.process_nodes(self.nodes, mock_summarizer, prompt)
            
            self.assertEqual(self.test_node.metadata.get('summary'), "这是一个测试摘要。")
            mock_summarizer.aget_response.assert_called_once()
        
        asyncio.run(test_process())

if __name__ == "__main__":
    unittest.main() 