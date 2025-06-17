"""
测试文档节点检索功能
"""
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.indices.index import build_tool_agents
from src.utils.node_display import display_retrieved_nodes, save_nodes_to_json, NodeDisplayer
from src.query_engine.enhanced_query_engine import create_enhanced_query_engine
from llama_index.core.indices import VectorStoreIndex
from llama_index.core.schema import QueryBundle

def test_direct_node_retrieval():
    """测试直接从增强查询引擎获取节点"""
    print("🔍 测试直接节点检索功能...")
    
    try:
        # 获取文档查询引擎
        doc_engines = build_tool_agents()
        
        if not doc_engines:
            print("❌ 没有可用的查询引擎")
            return
        
        # 使用第一个引擎进行测试
        first_category = next(iter(doc_engines.keys()))
        first_engine = doc_engines[first_category]
        
        print(f"✅ 使用引擎: {first_category}")
        
        # 测试查询
        test_queries = [
            "使用硬件控制模式，输出类型设置为 HCSL",
            "时钟输出频率配置",
            "芯片供电电压范围"
        ]
        
        for query in test_queries:
            print(f"\n{'='*60}")
            print(f"🔍 查询: {query}")
            print('='*60)
            
            # 方法1：通过普通查询获取节点
            response = first_engine.query(query)
            
            if hasattr(response, 'source_nodes') and response.source_nodes:
                print(f"\n📄 方法1：从查询响应中获取节点")
                display_retrieved_nodes(
                    response.source_nodes, 
                    query=query, 
                    show_summary=True
                )
                
                # 保存节点到JSON文件
                save_path = f"retrieved_nodes_{query[:10].replace(' ', '_')}.json"
                save_nodes_to_json(response.source_nodes, save_path)
            else:
                print("❌ 查询响应中没有source_nodes")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

def test_enhanced_query_engine_nodes():
    """测试增强查询引擎的专用节点获取方法"""
    print("\n🔧 测试增强查询引擎的节点获取方法...")
    
    try:
        # 这里我们需要创建一个单独的增强查询引擎来测试
        # 先获取文档
        from src.indices.index import load_nodes_from_disk
        from llama_index.core.indices import VectorStoreIndex
        
        docs = load_nodes_from_disk()
        if not docs:
            print("❌ 没有找到文档数据")
            return
        
        # 创建向量索引
        index = VectorStoreIndex(docs)
        
        # 创建增强查询引擎
        enhanced_engine = create_enhanced_query_engine(index)
        
        # 测试专用节点获取方法
        test_query = "HCSL输出类型"
        print(f"\n🔍 使用专用方法检索: {test_query}")
        
        # 使用新的get_retrieved_nodes方法
        nodes = enhanced_engine.get_retrieved_nodes(test_query)
        
        if nodes:
            print(f"\n📄 方法2：专用节点获取方法")
            display_retrieved_nodes(nodes, query=test_query, show_summary=True)
        else:
            print("❌ 没有检索到节点")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

def test_node_analysis():
    """测试节点分析功能"""
    print("\n📊 测试节点分析功能...")
    
    try:
        doc_engines = build_tool_agents()
        
        if not doc_engines:
            print("❌ 没有可用的查询引擎")
            return
        
        first_engine = next(iter(doc_engines.values()))
        
        # 执行查询
        response = first_engine.query("硬件控制 HCSL 输出配置")
        
        if hasattr(response, 'source_nodes') and response.source_nodes:
            # 创建节点显示器
            displayer = NodeDisplayer(max_content_length=300)
            
            # 获取详细统计
            summary = displayer.get_nodes_summary(response.source_nodes)
            
            print("\n📊 详细节点分析:")
            print(f"✓ 检索到的节点数量: {summary['total_nodes']}")
            print(f"✓ 平均相似度分数: {summary['avg_score']:.4f}")
            print(f"✓ 最高分数: {summary['max_score']:.4f}")
            print(f"✓ 最低分数: {summary['min_score']:.4f}")
            print(f"✓ 总内容长度: {summary['total_content_length']} 字符")
            
            # 显示分布情况
            if summary['doc_sources']:
                print(f"\n📚 文档来源分析:")
                for doc, count in summary['doc_sources'].items():
                    print(f"  • {doc}: {count} 个节点")
            
            if summary['categories']:
                print(f"\n🏷️ 类别分析:")
                for category, count in summary['categories'].items():
                    print(f"  • {category}: {count} 个节点")
            
            # 显示前3个最相关的节点
            print(f"\n🏆 Top 3 最相关节点:")
            sorted_nodes = sorted(
                response.source_nodes, 
                key=lambda x: x.score or 0, 
                reverse=True
            )
            
            for i, node in enumerate(sorted_nodes[:3], 1):
                content_preview = node.node.get_content()[:100] + "..."
                print(f"  {i}. 分数: {node.score:.4f} | 内容: {content_preview}")
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")
        import traceback
        traceback.print_exc()

def test_custom_node_filter():
    """测试自定义节点过滤"""
    print("\n🔧 测试自定义节点过滤...")
    
    try:
        doc_engines = build_tool_agents()
        
        if not doc_engines:
            print("❌ 没有可用的查询引擎")
            return
        
        first_engine = next(iter(doc_engines.values()))
        
        # 执行查询
        response = first_engine.query("时钟 频率 配置")
        
        if hasattr(response, 'source_nodes') and response.source_nodes:
            all_nodes = response.source_nodes
            
            print(f"📄 原始节点数量: {len(all_nodes)}")
            
            # 自定义过滤：只保留分数大于0.3的节点
            high_score_nodes = [
                node for node in all_nodes 
                if node.score and node.score > 0.3
            ]
            
            print(f"🎯 高分节点 (>0.3): {len(high_score_nodes)}")
            
            # 自定义过滤：只保留包含特定关键词的节点
            keyword_nodes = [
                node for node in all_nodes
                if any(keyword in node.node.get_content().lower() 
                      for keyword in ['时钟', 'clock', '频率', 'frequency'])
            ]
            
            print(f"🔍 关键词匹配节点: {len(keyword_nodes)}")
            
            # 显示过滤后的节点
            if high_score_nodes:
                print(f"\n📋 高分节点详情:")
                display_retrieved_nodes(high_score_nodes, show_summary=False)
        
    except Exception as e:
        print(f"❌ 过滤测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 开始测试文档节点检索功能")
    print("="*60)
    
    # 测试1：直接节点检索
    test_direct_node_retrieval()
    
    # 测试2：增强查询引擎专用方法
    test_enhanced_query_engine_nodes()
    
    # 测试3：节点分析
    test_node_analysis()
    
    # 测试4：自定义过滤
    test_custom_node_filter()
    
    print("\n✅ 所有测试完成！") 