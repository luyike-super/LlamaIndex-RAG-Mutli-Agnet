"""
简化的节点检索测试
"""
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.indices.index import build_tool_agents
from src.utils.node_display import display_retrieved_nodes

def test_basic_node_retrieval():
    """测试基本的节点检索功能"""
    print("🔍 测试基本节点检索功能")
    print("="*50)
    
    try:
        # 获取查询引擎
        print("🔄 加载查询引擎...")
        doc_engines = build_tool_agents()
        
        if not doc_engines:
            print("❌ 没有可用的查询引擎")
            return
        
        print(f"✅ 成功加载 {len(doc_engines)} 个查询引擎")
        
        # 获取第一个引擎
        first_category = next(iter(doc_engines.keys()))
        engine = doc_engines[first_category]
        
        print(f"🎯 使用引擎: {first_category[:50]}...")
        
        # 执行简单查询
        query = "HCSL"
        print(f"\n🔍 执行查询: {query}")
        
        response = engine.query(query)
        
        print(f"📝 响应类型: {type(response)}")
        print(f"📝 响应内容: {str(response)[:200]}...")
        
        # 检查是否有source_nodes
        if hasattr(response, 'source_nodes'):
            source_nodes = response.source_nodes
            print(f"✅ 找到 source_nodes 属性")
            print(f"📄 节点数量: {len(source_nodes) if source_nodes else 0}")
            
            if source_nodes:
                print(f"\n📋 节点详情:")
                for i, node in enumerate(source_nodes[:3], 1):
                    print(f"  节点 {i}:")
                    print(f"    分数: {node.score}")
                    print(f"    内容长度: {len(node.node.get_content())} 字符")
                    print(f"    内容预览: {node.node.get_content()[:100]}...")
                    print()
                
                # 使用节点显示工具
                print("="*50)
                print("使用专用显示工具:")
                display_retrieved_nodes(source_nodes, query, show_summary=True)
            else:
                print("⚠️ source_nodes 为空")
        else:
            print("❌ 响应中没有 source_nodes 属性")
            print(f"可用属性: {dir(response)}")
    
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_basic_node_retrieval() 