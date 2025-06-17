"""
直接测试增强查询引擎的节点返回功能
"""
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.indices.index import load_nodes_from_disk
from src.query_engine.enhanced_query_engine import create_enhanced_query_engine
from src.utils.node_display import display_retrieved_nodes
from llama_index.core.indices import VectorStoreIndex

def test_enhanced_engine_directly():
    """直接测试增强查询引擎"""
    print("🔧 直接测试增强查询引擎")
    print("="*50)
    
    try:
        # 1. 加载文档节点
        print("🔄 加载文档节点...")
        docs = load_nodes_from_disk()
        
        if not docs:
            print("❌ 没有找到文档节点")
            return
        
        print(f"✅ 成功加载 {len(docs)} 个文档节点")
        
        # 2. 创建向量索引
        print("🔄 创建向量索引...")
        vector_index = VectorStoreIndex(docs)
        print("✅ 向量索引创建成功")
        
        # 3. 创建增强查询引擎
        print("🔄 创建增强查询引擎...")
        enhanced_engine = create_enhanced_query_engine(vector_index)
        print("✅ 增强查询引擎创建成功")
        
        # 4. 测试查询
        test_queries = [
            "HCSL",
            "硬件控制",
            "输出类型",
            "时钟频率"
        ]
        
        for query in test_queries:
            print(f"\n{'='*60}")
            print(f"🔍 查询: {query}")
            print('='*60)
            
            # 方法1: 使用专用节点获取方法
            print(f"\n📄 方法1: 使用 get_retrieved_nodes()")
            nodes = enhanced_engine.get_retrieved_nodes(query)
            
            if nodes:
                print(f"✅ 检索到 {len(nodes)} 个节点")
                display_retrieved_nodes(nodes, query, show_summary=True)
            else:
                print("❌ 没有检索到任何节点")
            
            # 方法2: 使用标准查询方法
            print(f"\n📄 方法2: 使用标准 query() 方法")
            response = enhanced_engine.query(query)
            
            print(f"响应类型: {type(response)}")
            print(f"响应内容: {str(response)[:200]}...")
            
            if hasattr(response, 'source_nodes') and response.source_nodes:
                print(f"✅ 响应包含 {len(response.source_nodes)} 个源节点")
                
                # 比较两种方法的结果
                if nodes and response.source_nodes:
                    print(f"🔍 节点数量对比:")
                    print(f"  get_retrieved_nodes(): {len(nodes)}")
                    print(f"  query().source_nodes: {len(response.source_nodes)}")
                    
                    # 检查节点是否相同
                    same_nodes = len(nodes) == len(response.source_nodes)
                    if same_nodes:
                        for i, (n1, n2) in enumerate(zip(nodes, response.source_nodes)):
                            if n1.node.get_content() != n2.node.get_content():
                                same_nodes = False
                                break
                    
                    print(f"  节点内容是否相同: {'是' if same_nodes else '否'}")
            else:
                print("⚠️ 响应中没有源节点")
    
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

def test_node_metadata():
    """测试节点元数据显示"""
    print("\n📊 测试节点元数据显示")
    print("="*50)
    
    try:
        # 加载文档
        docs = load_nodes_from_disk()
        if not docs:
            print("❌ 没有找到文档节点")
            return
        
        # 创建索引和引擎
        vector_index = VectorStoreIndex(docs)
        enhanced_engine = create_enhanced_query_engine(vector_index)
        
        # 执行查询
        query = "HCSL硬件控制"
        nodes = enhanced_engine.get_retrieved_nodes(query)
        
        if nodes:
            print(f"✅ 检索到 {len(nodes)} 个节点")
            
            # 显示详细的节点信息
            for i, node_with_score in enumerate(nodes[:2], 1):
                node = node_with_score.node
                print(f"\n📋 节点 {i} 详细信息:")
                print(f"  🎯 分数: {node_with_score.score}")
                print(f"  🆔 节点ID: {getattr(node, 'node_id', 'N/A')}")
                print(f"  📚 文档ID: {getattr(node, 'ref_doc_id', 'N/A')}")
                
                if hasattr(node, 'metadata') and node.metadata:
                    print(f"  📊 元数据:")
                    for key, value in node.metadata.items():
                        print(f"    • {key}: {str(value)[:100]}...")
                
                content = node.get_content()
                print(f"  📝 内容长度: {len(content)} 字符")
                print(f"  📝 内容预览: {content[:200]}...")
        else:
            print("❌ 没有检索到节点")
    
    except Exception as e:
        print(f"❌ 元数据测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_enhanced_engine_directly()
    test_node_metadata() 