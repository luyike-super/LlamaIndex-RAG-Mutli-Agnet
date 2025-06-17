"""
排查查询引擎问题
"""
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_query_engine_directly():
    """直接测试查询引擎功能"""
    print("🔧 直接测试查询引擎功能...")
    
    try:
        from src.indices.index import load_nodes_from_disk, build_query_engine
        
        # 加载节点
        docs = load_nodes_from_disk()
        if not docs:
            print("❌ 没有加载到文档")
            return False
        
        print(f"✅ 加载到 {len(docs)} 个节点")
        
        # 构建查询引擎
        doc_engines = build_query_engine(docs)
        
        print(f"📊 查询引擎统计:")
        print(f"   by_id: {len(doc_engines['by_id'])} 个")
        print(f"   by_category: {len(doc_engines['by_category'])} 个类别")
        
        # 测试查询引擎
        for doc_id, engine in doc_engines['by_id'].items():
            print(f"\n🔍 测试文档 {doc_id} 的查询引擎...")
            
            try:
                # 直接调用查询引擎
                response = engine.query("HCSL")
                print(f"✅ 查询成功，响应长度: {len(str(response))} 字符")
                print(f"📝 响应预览: {str(response)[:200]}...")
                
                # 检查是否有源节点
                if hasattr(response, 'source_nodes') and response.source_nodes:
                    print(f"📄 检索到 {len(response.source_nodes)} 个源节点")
                    for i, node in enumerate(response.source_nodes[:3]):
                        score = getattr(node, 'score', 'N/A')
                        content_preview = node.node.get_content()[:100] if hasattr(node.node, 'get_content') else str(node.node)[:100]
                        print(f"   节点 {i+1}: 分数={score}, 内容={content_preview}...")
                else:
                    print("⚠️ 没有检索到源节点")
                
                return True
                
            except Exception as query_error:
                print(f"❌ 查询失败: {query_error}")
                import traceback
                traceback.print_exc()
                return False
        
        return False
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_vector_index_directly():
    """直接测试向量索引"""
    print("\n🔧 直接测试向量索引...")
    
    try:
        from src.indices.index import load_nodes_from_disk
        from llama_index.core.indices import VectorStoreIndex
        from config.config_rag import RETRIEVAL_CONFIG
        
        # 加载节点
        docs = load_nodes_from_disk()
        if not docs:
            print("❌ 没有加载到文档")
            return False
        
        print(f"✅ 加载到 {len(docs)} 个节点")
        
        # 创建简单的向量索引
        vector_index = VectorStoreIndex(docs[:5])  # 只用前5个节点测试
        
        # 创建简单的查询引擎
        query_engine = vector_index.as_query_engine(
            similarity_top_k=RETRIEVAL_CONFIG.get("similarity_top_k", 3)
        )
        
        # 测试查询
        response = query_engine.query("HCSL")
        print(f"✅ 查询成功，响应: {str(response)[:200]}...")
        
        # 检查源节点
        if hasattr(response, 'source_nodes') and response.source_nodes:
            print(f"📄 检索到 {len(response.source_nodes)} 个源节点")
            return True
        else:
            print("⚠️ 没有检索到源节点")
            return False
        
    except Exception as e:
        print(f"❌ 向量索引测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_enhanced_query_engine():
    """测试增强查询引擎是否有问题"""
    print("\n🔧 测试增强查询引擎...")
    
    try:
        from src.indices.index import load_nodes_from_disk
        from llama_index.core.indices import VectorStoreIndex
        from src.query_engine.enhanced_query_engine import create_enhanced_query_engine
        
        # 加载节点
        docs = load_nodes_from_disk()
        if not docs:
            print("❌ 没有加载到文档")
            return False
        
        # 创建向量索引
        vector_index = VectorStoreIndex(docs[:5])
        
        # 测试增强查询引擎
        try:
            enhanced_engine = create_enhanced_query_engine(vector_index)
            print("✅ 增强查询引擎创建成功")
            
            # 测试查询
            response = enhanced_engine.query("HCSL")
            print(f"✅ 增强引擎查询成功: {str(response)[:200]}...")
            return True
            
        except Exception as enhanced_error:
            print(f"❌ 增强查询引擎失败: {enhanced_error}")
            
            # 回退到简单查询引擎
            simple_engine = vector_index.as_query_engine(similarity_top_k=3)
            response = simple_engine.query("HCSL")
            print(f"✅ 简单引擎查询成功: {str(response)[:200]}...")
            return True
        
    except Exception as e:
        print(f"❌ 增强查询引擎测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 开始排查查询引擎问题")
    print("="*60)
    
    success_count = 0
    total_tests = 3
    
    # 测试1：直接测试查询引擎
    if test_query_engine_directly():
        success_count += 1
    
    # 测试2：测试向量索引
    if test_vector_index_directly():
        success_count += 1
    
    # 测试3：测试增强查询引擎
    if test_enhanced_query_engine():
        success_count += 1
    
    print(f"\n📊 排查结果总结:")
    print(f"   成功: {success_count}/{total_tests}")
    
    if success_count > 0:
        print("🎉 至少有部分功能正常！")
    else:
        print("❌ 所有测试都失败，需要深入排查") 