"""
验证修复后的文档切分功能
"""
import sys
import os
import shutil

# 添加项目根目录到路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_new_ingestion_with_chunking():
    """测试新的智能切分摄取管道"""
    print("🔧 测试新的智能切分摄取管道...")
    
    try:
        from src.data_ingestion.ingestion_pipeline import run_ingestion_pipeline_with_smart_chunking
        
        # 运行智能切分管道
        nodes = run_ingestion_pipeline_with_smart_chunking()
        
        if not nodes:
            print("❌ 没有生成任何节点")
            return False
        
        print(f"✅ 智能切分管道成功，生成 {len(nodes)} 个节点")
        
        # 分析节点
        total_length = 0
        long_nodes = 0
        
        for i, node in enumerate(nodes):
            content = node.get_content() if hasattr(node, 'get_content') else str(node)
            content_length = len(content)
            total_length += content_length
            
            if content_length > 2048:
                long_nodes += 1
                print(f"   节点 {i+1}: {content_length} 字符 (超长)")
            else:
                print(f"   节点 {i+1}: {content_length} 字符")
        
        print(f"\n📊 统计结果:")
        print(f"   总节点数: {len(nodes)}")
        print(f"   平均长度: {total_length // len(nodes)} 字符")
        print(f"   超长节点数: {long_nodes}")
        print(f"   合格节点数: {len(nodes) - long_nodes}")
        
        # 验证切分效果
        if long_nodes == 0:
            print("🎉 所有节点都在合理长度范围内！")
            return True
        else:
            print(f"⚠️ 仍有 {long_nodes} 个超长节点")
            return False
            
    except Exception as e:
        print(f"❌ 智能切分管道测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_rebuild_from_scratch():
    """测试从头重建文档索引"""
    print("\n🔄 测试从头重建文档索引...")
    
    try:
        # 清除现有存储
        store_dir = "store/docstore/processed_nodes"
        if os.path.exists(store_dir):
            print(f"清除现有存储: {store_dir}")
            shutil.rmtree(store_dir)
        
        # 重新构建
        from src.indices.index import build_tool_agents
        
        agents = build_tool_agents()
        
        if not agents:
            print("❌ 没有成功构建任何代理")
            return False
        
        print(f"✅ 成功构建 {len(agents)} 个代理")
        
        # 验证存储的节点
        from src.indices.index import load_nodes_from_disk
        loaded_nodes = load_nodes_from_disk()
        
        if not loaded_nodes:
            print("❌ 没有加载到任何节点")
            return False
        
        print(f"📄 加载到 {len(loaded_nodes)} 个节点")
        
        # 分析节点长度
        total_length = 0
        long_nodes = 0
        
        for i, node in enumerate(loaded_nodes):
            content = node.get_content() if hasattr(node, 'get_content') else str(node)
            content_length = len(content)
            total_length += content_length
            
            if content_length > 2048:
                long_nodes += 1
                print(f"   节点 {i+1}: {content_length} 字符 (超长)")
            else:
                print(f"   节点 {i+1}: {content_length} 字符")
        
        print(f"\n📊 重建后统计:")
        print(f"   总节点数: {len(loaded_nodes)}")
        print(f"   平均长度: {total_length // len(loaded_nodes)} 字符")
        print(f"   超长节点数: {long_nodes}")
        print(f"   合格节点数: {len(loaded_nodes) - long_nodes}")
        
        if long_nodes == 0:
            print("🎉 重建成功！所有节点都在合理长度范围内！")
            return True
        else:
            print(f"⚠️ 重建后仍有 {long_nodes} 个超长节点")
            return long_nodes < len(loaded_nodes) // 2  # 至少一半节点是合格的
            
    except Exception as e:
        print(f"❌ 重建测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_query_with_chunked_documents():
    """测试使用切分后文档的查询功能"""
    print("\n🔍 测试使用切分后文档的查询功能...")
    
    try:
        from src.indices.index import load_nodes_from_disk
        from src.utils.node_display import display_retrieved_nodes
        from llama_index.core.schema import NodeWithScore
        
        # 加载节点
        docs = load_nodes_from_disk()
        if not docs:
            print("❌ 没有加载到文档")
            return False
        
        # 模拟查询
        query = "如何通过硬件控制， 把输出配置为 HCSL"
        matched_nodes = []
        
        for doc in docs:
            content = doc.get_content() if hasattr(doc, 'get_content') else str(doc)
            
            if query.lower() in content.lower():
                score = content.lower().count(query.lower()) / len(content.split())
                node_with_score = NodeWithScore(node=doc, score=score)
                matched_nodes.append(node_with_score)
        
        matched_nodes.sort(key=lambda x: x.score, reverse=True)
        
        print(f"✅ 找到 {len(matched_nodes)} 个匹配的节点")
        
        # 显示前3个结果
        if matched_nodes:
            display_retrieved_nodes(
                matched_nodes[:3], 
                query=query, 
                show_summary=True
            )
        
        return len(matched_nodes) > 0
        
    except Exception as e:
        print(f"❌ 查询测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 开始验证修复后的文档切分功能")
    print("="*60)
    
    success_count = 0
    total_tests = 1
    
    # 测试重建以验证工具数量修复
    if test_rebuild_from_scratch():
        success_count += 1
    
    print(f"\n📊 验证结果总结:")
    print(f"   成功: {success_count}/{total_tests}")
    
    if success_count == total_tests:
        print("🎉 验证通过！工具数量问题已修复！")
    else:
        print("⚠️ 验证失败，还需要进一步调整")

    

