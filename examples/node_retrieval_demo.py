"""
文档节点检索功能使用示例
"""
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.indices.index import build_tool_agents
from src.utils.node_display import display_retrieved_nodes

def simple_node_retrieval_demo():
    """简单的节点检索演示"""
    print("📚 文档节点检索功能演示")
    print("="*50)
    
    # 1. 加载查询引擎
    print("🔄 正在加载文档查询引擎...")
    doc_engines = build_tool_agents()
    
    if not doc_engines:
        print("❌ 没有可用的查询引擎")
        return
    
    print(f"✅ 成功加载 {len(doc_engines)} 个查询引擎")
    
    # 2. 选择一个引擎进行演示
    first_category = next(iter(doc_engines.keys()))
    engine = doc_engines[first_category]
    
    print(f"🎯 使用引擎: {first_category[:50]}...")
    
    # 3. 执行查询并获取节点
    query = "硬件控制模式设置HCSL输出类型"
    print(f"\n🔍 查询: {query}")
    
    # 执行查询
    response = engine.query(query)
    
    # 4. 显示检索到的节点
    if hasattr(response, 'source_nodes') and response.source_nodes:
        print(f"\n✅ 检索成功！找到 {len(response.source_nodes)} 个相关节点")
        
        # 使用我们的节点显示工具
        display_retrieved_nodes(
            response.source_nodes, 
            query=query, 
            show_summary=True
        )
        
        print(f"\n📝 AI生成的回答:")
        print(f"{response}")
        
    else:
        print("❌ 没有检索到相关节点")

def interactive_node_search():
    """交互式节点搜索"""
    print("\n🔍 交互式节点搜索")
    print("="*50)
    
    # 加载引擎
    doc_engines = build_tool_agents()
    
    if not doc_engines:
        print("❌ 没有可用的查询引擎")
        return
    
    engine = next(iter(doc_engines.values()))
    
    while True:
        # 获取用户输入
        user_query = input("\n请输入查询内容 (输入'quit'退出): ").strip()
        
        if user_query.lower() in ['quit', 'exit', '退出', 'q']:
            print("👋 再见！")
            break
        
        if not user_query:
            print("⚠️ 请输入有效的查询内容")
            continue
        
        try:
            # 执行查询
            print(f"\n🔍 正在搜索: {user_query}")
            response = engine.query(user_query)
            
            if hasattr(response, 'source_nodes') and response.source_nodes:
                # 显示检索节点
                display_retrieved_nodes(
                    response.source_nodes, 
                    query=user_query, 
                    show_summary=True
                )
                
                print(f"\n🤖 AI回答: {response}")
            else:
                print("❌ 没有找到相关信息")
                
        except Exception as e:
            print(f"❌ 搜索出错: {e}")

if __name__ == "__main__":
    # 运行简单演示
    simple_node_retrieval_demo()
    
    # 运行交互式搜索（可选）
    print("\n" + "="*60)
    choice = input("是否要尝试交互式搜索？(y/n): ").strip().lower()
    
    if choice in ['y', 'yes', '是', '好']:
        interactive_node_search()
    else:
        print("✅ 演示完成！") 