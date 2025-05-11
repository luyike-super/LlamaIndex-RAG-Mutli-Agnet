import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import os
import shutil
from src.data_ingestion.ingestion_pipeline import (
    run_ingestion_pipeline,
    create_pipeline,
    save_nodes_to_disk,
    load_nodes_from_disk,
    STORAGE_DIR,
    ensure_storage_dir_exists
)
from llama_index.core import Document

class MockTransformPipeline:
    """模拟转换管道，跳过可能出错的转换步骤"""
    def __init__(self):
        self.transformations = []
    
    def run(self, documents):
        """直接返回文档转换为节点"""
        from llama_index.core.node_parser import SentenceSplitter
        parser = SentenceSplitter()
        return parser.get_nodes_from_documents(documents)

class TestIngestionPipelinePersistence(unittest.TestCase):
    """测试数据摄入管道的持久化功能"""
    
    def setUp(self):
        """测试前的准备工作"""
        # 确保存储目录存在
        ensure_storage_dir_exists()
        # 创建测试文档，添加必要的metadata
        self.test_documents = [
            Document(
                text="这是测试文档1，用于测试数据摄入管道。",
                metadata={"file_path": "test/doc1.md", "source": "test"}
            ),
            Document(
                text="这是测试文档2，包含一些关键信息和URL: https://example.com",
                metadata={"file_path": "test/doc2.md", "source": "test"}
            ),
            Document(
                text="这是测试文档3，测试分类提取功能。这是一篇关于人工智能的文章。",
                metadata={"file_path": "test/doc3.md", "source": "test"}
            )
        ]
        
        # 备份原始处理管道创建函数
        self.original_create_pipeline = create_pipeline
        
        # 清理可能存在的测试节点文件
        for file_name in ["processed_nodes.pkl", "test_nodes.pkl"]:
            file_path = os.path.join(STORAGE_DIR, file_name)
            if os.path.exists(file_path):
                os.remove(file_path)
    
    def tearDown(self):
        """测试后的清理工作"""
        # 清理测试产生的文件
        for file_name in ["processed_nodes.pkl", "test_nodes.pkl"]:
            file_path = os.path.join(STORAGE_DIR, file_name)
            if os.path.exists(file_path):
                os.remove(file_path)
    
    def test_create_pipeline(self):
        """测试创建管道功能"""
        pipeline = create_pipeline()
        self.assertIsNotNone(pipeline)
        self.assertTrue(hasattr(pipeline, "run"))
        self.assertTrue(len(pipeline.transformations) > 0)
    
    def test_run_pipeline_with_documents(self):
        """测试使用提供的文档运行管道"""
        # 使用 monkeypatch 替换创建管道的函数，避免转换错误
        import src.data_ingestion.ingestion_pipeline as module
        original_create_pipeline = module.create_pipeline
        
        try:
            # 替换为简单的管道创建函数
            module.create_pipeline = lambda: MockTransformPipeline()
            
            # 运行管道
            nodes = run_ingestion_pipeline(documents=self.test_documents)
            self.assertIsNotNone(nodes)
            self.assertTrue(len(nodes) > 0)
            # 检查节点是否包含原始文档的内容
            all_text = " ".join([node.get_content() for node in nodes])
            self.assertIn("测试文档", all_text)
        finally:
            # 恢复原始函数
            module.create_pipeline = original_create_pipeline
    
    def test_save_and_load_nodes(self):
        """测试节点的保存和加载功能"""
        # 使用 monkeypatch 替换创建管道的函数，避免转换错误
        import src.data_ingestion.ingestion_pipeline as module
        original_create_pipeline = module.create_pipeline
        
        try:
            # 替换为简单的管道创建函数
            module.create_pipeline = lambda: MockTransformPipeline()
            
            # 运行管道处理文档
            nodes = run_ingestion_pipeline(documents=self.test_documents)
            
            # 使用特定文件名保存节点
            save_result = save_nodes_to_disk(nodes, "test_nodes.pkl")
            self.assertTrue(save_result)
            
            # 加载保存的节点
            loaded_nodes = load_nodes_from_disk("test_nodes.pkl")
            self.assertIsNotNone(loaded_nodes)
            self.assertEqual(len(nodes), len(loaded_nodes))
        finally:
            # 恢复原始函数
            module.create_pipeline = original_create_pipeline
    
    def test_persistence_workflow(self):
        """测试完整的持久化工作流程"""
        # 使用 monkeypatch 替换创建管道的函数，避免转换错误
        import src.data_ingestion.ingestion_pipeline as module
        original_create_pipeline = module.create_pipeline
        
        try:
            # 替换为简单的管道创建函数
            module.create_pipeline = lambda: MockTransformPipeline()
            
            # 第一次运行，处理文档并保存
            nodes1 = run_ingestion_pipeline(documents=self.test_documents)
            self.assertTrue(len(nodes1) > 0)
            
            # 第二次运行，应该直接从持久化存储加载
            nodes2 = run_ingestion_pipeline()
            self.assertEqual(len(nodes1), len(nodes2))
            
            # 检查两次返回的节点内容是否相同
            for i in range(len(nodes1)):
                self.assertEqual(nodes1[i].get_content(), nodes2[i].get_content())
        finally:
            # 恢复原始函数
            module.create_pipeline = original_create_pipeline

if __name__ == "__main__":
    unittest.main() 