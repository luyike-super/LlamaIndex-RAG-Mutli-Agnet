"""
最简单的节点返回功能验证
"""
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_basic_document_loading():
    """测试基础文档加载功能"""
    print("🔍 测试基础文档加载...")
    
    try:
        from src.indices.index import load_nodes_from_disk
        
        # 直接从磁盘加载节点
        docs = load_nodes_from_disk()
        
        if docs is None:
            print("❌ 没有找到持久化的文档节点")
            return False
        
        if len(docs) == 0:
            print("❌ 文档节点列表为空")
            return False
        
        print(f"✅ 成功加载 {len(docs)} 个文档节点")
        
        # 检查第一个文档的基本信息
        first_doc = docs[0]
        print(f"\n📋 第一个文档节点信息:")
        print(f"   类型: {type(first_doc)}")
        print(f"   ID: {getattr(first_doc, 'id_', 'N/A')}")
        print(f"   节点ID: {getattr(first_doc, 'node_id', 'N/A')}")
        
        # 获取内容长度
        if hasattr(first_doc, 'get_content'):
            content = first_doc.get_content()
            print(f"   内容长度: {len(content)} 字符")
            print(f"   内容预览: {content[:200]}...")
        elif hasattr(first_doc, 'text'):
            text = first_doc.text
            print(f"   文本长度: {len(text)} 字符")
            print(f"   文本预览: {text[:200]}...")
        
        # 检查元数据
        if hasattr(first_doc, 'metadata') and first_doc.metadata:
            print(f"   元数据: {first_doc.metadata}")
        
        return True
        
    except Exception as e:
        print(f"❌ 文档加载测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_document_content_analysis():
    """分析文档内容，检查是否存在长度问题"""
    print("\n📊 分析文档内容...")
    
    try:
        from src.indices.index import load_nodes_from_disk
        
        docs = load_nodes_from_disk()
        if not docs:
            print("❌ 没有文档可分析")
            return False
        
        print(f"📄 分析 {len(docs)} 个文档节点:")
        
        total_length = 0
        long_docs = 0
        empty_docs = 0
        
        for i, doc in enumerate(docs):
            # 获取内容
            content = ""
            if hasattr(doc, 'get_content'):
                content = doc.get_content()
            elif hasattr(doc, 'text'):
                content = doc.text
            elif hasattr(doc, 'content'):
                content = doc.content
            
            content_length = len(content)
            total_length += content_length
            
            if content_length == 0:
                empty_docs += 1
                print(f"   ⚠️ 文档 {i+1}: 内容为空")
            elif content_length > 2048:
                long_docs += 1
                print(f"   📏 文档 {i+1}: {content_length} 字符 (超过2048限制)")
            else:
                print(f"   ✅ 文档 {i+1}: {content_length} 字符 (符合要求)")
        
        print(f"\n📊 统计结果:")
        print(f"   总文档数: {len(docs)}")
        print(f"   平均长度: {total_length // len(docs)} 字符")
        print(f"   空文档数: {empty_docs}")
        print(f"   超长文档数: {long_docs}")
        print(f"   合格文档数: {len(docs) - empty_docs - long_docs}")
        
        return True
        
    except Exception as e:
        print(f"❌ 内容分析失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_simple_retrieval_without_embedding():
    """测试不依赖嵌入的简单检索"""
    print("\n🔍 测试简单文本匹配检索...")
    
    try:
        from src.indices.index import load_nodes_from_disk
        from llama_index.core.schema import NodeWithScore
        
        docs = load_nodes_from_disk()
        if not docs:
            print("❌ 没有文档可检索")
            return False
        
        # 简单的关键词匹配
        query = "HCSL"
        print(f"🔍 搜索关键词: {query}")
        
        matched_nodes = []
        
        for doc in docs:
            # 获取内容
            content = ""
            if hasattr(doc, 'get_content'):
                content = doc.get_content()
            elif hasattr(doc, 'text'):
                content = doc.text
            
            # 简单的关键词匹配
            if query.lower() in content.lower():
                # 计算简单的匹配分数（关键词出现次数）
                score = content.lower().count(query.lower()) / len(content.split())
                
                # 创建NodeWithScore对象
                node_with_score = NodeWithScore(node=doc, score=score)
                matched_nodes.append(node_with_score)
        
        # 按分数排序
        matched_nodes.sort(key=lambda x: x.score, reverse=True)
        
        print(f"✅ 找到 {len(matched_nodes)} 个匹配的节点")
        
        # 显示前3个结果
        for i, node_with_score in enumerate(matched_nodes[:3], 1):
            node = node_with_score.node
            content = node.get_content() if hasattr(node, 'get_content') else str(node)
            
            print(f"\n📋 匹配节点 {i}:")
            print(f"   分数: {node_with_score.score:.4f}")
            print(f"   内容长度: {len(content)} 字符")
            print(f"   内容预览: {content[:150]}...")
        
        return len(matched_nodes) > 0
        
    except Exception as e:
        print(f"❌ 简单检索测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_node_display_functionality():
    """测试节点显示功能"""
    print("\n🎨 测试节点显示功能...")
    
    try:
        from src.indices.index import load_nodes_from_disk
        from src.utils.node_display import display_retrieved_nodes, NodeDisplayer
        from llama_index.core.schema import NodeWithScore
        
        docs = load_nodes_from_disk()
        if not docs:
            print("❌ 没有文档可显示")
            return False
        
        # 创建模拟的NodeWithScore列表
        mock_nodes = []
        for i, doc in enumerate(docs[:2]):  # 只取前2个文档
            score = 0.8 - i * 0.1  # 模拟分数
            node_with_score = NodeWithScore(node=doc, score=score)
            mock_nodes.append(node_with_score)
        
        print(f"✅ 创建了 {len(mock_nodes)} 个模拟节点")
        
        # 测试显示功能
        display_retrieved_nodes(
            mock_nodes, 
            query="测试查询", 
            show_summary=True
        )
        
        return True
        
    except Exception as e:
        print(f"❌ 节点显示测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 开始最简单的节点返回功能验证")
    print("="*60)
    
    # 激活conda环境提示
    print("⚠️ 请确保已激活 llamaindex 环境：conda activate llamaindex")
    print()
    
    success_count = 0
    total_tests = 4
    
    # 测试1：基础文档加载
    if test_basic_document_loading():
        success_count += 1
    
    # 测试2：文档内容分析
    if test_document_content_analysis():
        success_count += 1
    
    # 测试3：简单检索（不使用嵌入）
    if test_simple_retrieval_without_embedding():
        success_count += 1
    
    # 测试4：节点显示功能
    if test_node_display_functionality():
        success_count += 1
    
    print(f"\n📊 测试结果总结:")
    print(f"   成功: {success_count}/{total_tests}")
    print(f"   失败: {total_tests - success_count}/{total_tests}")
    
    if success_count == total_tests:
        print("🎉 所有测试通过！节点返回功能验证成功！")
    else:
        print("⚠️ 部分测试失败，请检查相关功能") 