import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.indices.index import test_load_docs, build_document_agents, build_category_agents
from src.models import LLMFactory, LLMProviderType
from src.data_ingestion.ingestion_pipeline import run_ingestion_pipeline


def test_document_loading():
    """测试文档加载功能"""
    print("===== 测试文档加载 =====")
    docs = run_ingestion_pipeline()
    print(f"成功加载文档数量: {len(docs)}")
    if len(docs) > 0:
        print(f"第一个文档ID: {docs[0].id_}")
        print(f"第一个文档内容片段: {docs[0].text[:100]}...")
    return docs


def test_document_agents():
    """测试创建文档代理"""
    print("\n===== 测试文档代理创建 =====")
    docs = run_ingestion_pipeline()
    doc_agents = build_document_agents(docs)
    print(f"成功创建文档代理数量: {len(doc_agents)}")
    print(f"文档代理ID列表: {list(doc_agents.keys())[:5]}...")
    return doc_agents


def test_category_agents():
    """测试创建类别代理"""
    print("\n===== 测试类别代理创建 =====")
    doc_agents = test_document_agents()
    
    # 创建测试用的类别映射
    # 假设我们使用前两个文档ID作为安装指南类别，后两个作为API文档类别
    doc_ids = list(doc_agents.keys())
    categories = {
        "安装指南": doc_ids[:2] if len(doc_ids) >= 2 else doc_ids[:1],
        "API文档": doc_ids[2:4] if len(doc_ids) >= 4 else doc_ids[1:2]
    }
    
    print(f"创建的类别映射: {categories}")
    
    category_agents = build_category_agents(doc_agents, categories)
    print(f"成功创建类别代理数量: {len(category_agents)}")
    print(f"类别代理列表: {list(category_agents.keys())}")
    return category_agents


def test_query_document_agent():
    """测试文档代理查询"""
    print("\n===== 测试文档代理查询 =====")
    doc_agents = test_document_agents()
    
    if not doc_agents:
        print("没有可用的文档代理进行测试")
        return
    
    # 选择第一个文档代理进行测试
    first_doc_id = list(doc_agents.keys())[0]
    test_query = "LlamaIndex是什么?"
    
    print(f"使用文档 {first_doc_id} 查询: '{test_query}'")
    try:
        response = doc_agents[first_doc_id].query(test_query)
        print(f"查询响应: {response}")
    except Exception as e:
        print(f"查询出错: {str(e)}")


def test_query_category_agent():
    """测试类别代理查询"""
    print("\n===== 测试类别代理查询 =====")
    category_agents = test_category_agents()
    
    if not category_agents:
        print("没有可用的类别代理进行测试")
        return
    
    # 选择第一个类别代理进行测试
    first_category = list(category_agents.keys())[0]
    test_query = "如何使用LlamaIndex?"
    
    print(f"使用类别 {first_category} 查询: '{test_query}'")
    try:
        response = category_agents[first_category].chat(test_query)
        print(f"查询响应: {response}")
    except Exception as e:
        print(f"查询出错: {str(e)}")


if __name__ == "__main__":
    print("开始LlamaIndex代理测试...\n")
    
    # 测试1: 文档加载
    docs = test_document_loading()
    
    # 测试2: 文档代理创建
    doc_agents = test_document_agents()
    
    # 测试3: 类别代理创建
    category_agents = test_category_agents()
    
    # 测试4: 文档代理查询
    test_query_document_agent()
    
    # 测试5: 类别代理查询
    test_query_category_agent()
    
    print("\n所有测试完成!")
    

