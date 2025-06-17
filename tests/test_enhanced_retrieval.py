"""
增强检索功能测试
"""
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data_ingestion import run_ingestion_pipeline
from src.indices.index import build_tool_agents
from src.utils.retrieval_evaluator import RetrievalEvaluator, create_test_queries
from config.config_rag import RETRIEVAL_CONFIG

def test_enhanced_retrieval():
    """测试增强检索功能"""
    print("开始测试增强检索功能...")
    
    # 1. 获取文档查询引擎
    print("正在加载文档查询引擎...")
    try:
        doc_engines = build_tool_agents()
        print(f"成功加载 {len(doc_engines)} 个文档查询引擎")
    except Exception as e:
        print(f"加载文档查询引擎失败: {e}")
        return
    
    if not doc_engines:
        print("没有可用的查询引擎，测试终止")
        return
    
    # 2. 创建评估器
    evaluator = RetrievalEvaluator()
    
    # 3. 创建测试查询
    test_queries = create_test_queries()
    
    # 4. 对每个查询引擎进行评估
    all_results = {}
    
    for doc_id, engine in list(doc_engines.items())[:3]:  # 只测试前3个引擎
        print(f"\n正在测试文档 {doc_id} 的查询引擎...")
        
        # 运行评估套件
        evaluation_result = evaluator.run_evaluation_suite(
            test_queries=test_queries,
            query_engine=engine
        )
        
        all_results[doc_id] = evaluation_result
        
        # 打印评估报告
        print(f"\n=== 文档 {doc_id} 的评估结果 ===")
        evaluator.print_evaluation_report(evaluation_result)
    
    # 5. 打印配置信息
    print("\n" + "="*50)
    print("当前检索配置:")
    print("="*50)
    print(f"• 相似度检索数量: {RETRIEVAL_CONFIG.get('similarity_top_k', 'N/A')}")
    print(f"• 相似度阈值: {RETRIEVAL_CONFIG.get('similarity_cutoff', 'N/A')}")
    print(f"• 启用重排序: {RETRIEVAL_CONFIG.get('enable_reranking', 'N/A')}")
    print(f"• 重排序保留数量: {RETRIEVAL_CONFIG.get('rerank_top_k', 'N/A')}")
    print(f"• 启用混合检索: {RETRIEVAL_CONFIG.get('enable_hybrid_search', 'N/A')}")
    
    # 6. 提供改进建议
    print("\n" + "="*50)
    print("检索效果改进建议:")
    print("="*50)
    
    # 分析综合结果
    avg_scores = []
    avg_coverage = []
    avg_query_times = []
    
    for doc_id, result in all_results.items():
        if "summary" in result:
            summary = result["summary"]
            avg_scores.append(summary.get("avg_avg_score", 0))
            avg_coverage.append(summary.get("avg_keyword_coverage", 0))
            avg_query_times.append(summary.get("avg_query_time", 0))
    
    if avg_scores:
        overall_avg_score = sum(avg_scores) / len(avg_scores)
        overall_avg_coverage = sum(avg_coverage) / len(avg_coverage)
        overall_avg_time = sum(avg_query_times) / len(avg_query_times)
        
        print(f"\n📊 综合表现:")
        print(f"• 平均相似度分数: {overall_avg_score:.3f}")
        print(f"• 平均关键词覆盖率: {overall_avg_coverage*100:.1f}%")
        print(f"• 平均查询时间: {overall_avg_time:.2f}秒")
        
        print(f"\n💡 建议:")
        
        if overall_avg_score < 0.7:
            print("• 相似度分数较低，建议:")
            print("  - 调整embedding模型参数")
            print("  - 优化文档分块策略")
            print("  - 增加同义词扩展")
        
        if overall_avg_coverage < 0.6:
            print("• 关键词覆盖率较低，建议:")
            print("  - 启用查询扩展功能")
            print("  - 优化重排序算法")
            print("  - 增加检索数量(similarity_top_k)")
        
        if overall_avg_time > 2.0:
            print("• 查询时间较长，建议:")
            print("  - 优化索引结构")
            print("  - 减少后处理步骤")
            print("  - 使用更快的embedding模型")
        
        print(f"\n🔧 推荐配置调整:")
        
        if overall_avg_coverage < 0.5:
            print("• 增加similarity_top_k到15-20")
            print("• 降低similarity_cutoff到0.6")
            print("• 增加rerank_top_k到8-10")
        
        if overall_avg_score < 0.6:
            print("• 调整文档分块大小:")
            print("  - Markdown: chunk_size=600, chunk_overlap=120")
            print("  - Word: chunk_size=1000, chunk_overlap=200")
            print("  - 默认: chunk_size=800, chunk_overlap=160")

def test_single_query_detailed():
    """详细测试单个查询"""
    print("\n" + "="*50)
    print("详细单查询测试")
    print("="*50)
    
    try:
        doc_engines = build_tool_agents()
        if not doc_engines:
            print("没有可用的查询引擎")
            return
        
        # 使用第一个引擎进行详细测试
        first_engine = next(iter(doc_engines.values()))
        
        test_query = "使用硬件控制模式，输出类型设置为 HCSL"
        
        print(f"测试查询: {test_query}")
        
        # 执行查询
        response = first_engine.query(test_query)
        
        print(f"\n响应结果:")
        print(f"响应长度: {len(str(response))} 字符")
        print(f"响应内容: {str(response)[:500]}...")
        
        # 分析检索到的节点
        if hasattr(response, 'source_nodes') and response.source_nodes:
            print(f"\n检索到的节点数量: {len(response.source_nodes)}")
            
            for i, node in enumerate(response.source_nodes[:3], 1):
                print(f"\n节点 {i}:")
                print(f"  相似度分数: {node.score:.3f}")
                print(f"  内容长度: {len(node.node.get_content())} 字符")
                print(f"  内容预览: {node.node.get_content()[:200]}...")
        
    except Exception as e:
        print(f"详细测试失败: {e}")

if __name__ == "__main__":
    print("启动增强检索功能测试...")
    
    # 运行主要测试
    test_enhanced_retrieval()
    
    # 运行详细测试
    test_single_query_detailed()
    
    print("\n测试完成！") 