"""
Word文档切分功能测试
"""
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_word_parser_configuration():
    """测试Word解析器配置是否正确"""
    print("🔧 测试Word解析器配置...")
    
    try:
        from config.config_rag import CHUNKING_CONFIG
        from src.node_parser.word_parser import WordNodeParser
        
        # 检查配置
        docx_config = CHUNKING_CONFIG.get("docx", {})
        print(f"📋 docx配置: {docx_config}")
        
        # 创建解析器
        parser = WordNodeParser(
            chunk_size=docx_config.get("chunk_size", 1024),
            chunk_overlap=docx_config.get("chunk_overlap", 150)
        )
        
        print(f"✅ 解析器创建成功")
        print(f"   chunk_size: {parser.chunk_size}")
        print(f"   chunk_overlap: {parser.chunk_overlap}")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_word_chunking_with_mock_document():
    """使用模拟文档测试Word切分功能"""
    print("\n📄 测试Word文档切分功能...")
    
    try:
        from llama_index.core.schema import Document
        from src.node_parser.word_parser import WordNodeParser
        from config.config_rag import CHUNKING_CONFIG
        
        # 创建一个长文本模拟Word文档内容
        long_text = "这是一个测试文档。" * 500  # 大约7000字符
        
        # 创建模拟文档
        mock_doc = Document(
            text=long_text,
            metadata={
                'file_name': 'test.docx',
                'file_type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            }
        )
        
        print(f"📋 模拟文档信息:")
        print(f"   长度: {len(long_text)} 字符")
        print(f"   文件名: {mock_doc.metadata['file_name']}")
        
        # 获取配置
        config = CHUNKING_CONFIG.get("docx", CHUNKING_CONFIG["default"])
        print(f"📋 使用配置: {config}")
        
        # 创建解析器
        parser = WordNodeParser(
            chunk_size=config["chunk_size"],
            chunk_overlap=config["chunk_overlap"]
        )
        
        # 执行切分
        nodes = parser.get_nodes_from_documents([mock_doc])
        
        print(f"\n📊 切分结果:")
        print(f"   生成节点数: {len(nodes)}")
        
        # 分析每个节点
        total_length = 0
        for i, node in enumerate(nodes):
            content_length = len(node.get_content())
            total_length += content_length
            print(f"   节点 {i+1}: {content_length} 字符")
            if hasattr(node, 'metadata') and 'parser_type' in node.metadata:
                print(f"      解析器类型: {node.metadata['parser_type']}")
        
        print(f"   总长度: {total_length} 字符")
        print(f"   预期节点数: {len(long_text) // config['chunk_size'] + 1}")
        
        # 验证是否正确切分
        expected_chunks = max(1, len(long_text) // config["chunk_size"])
        if len(nodes) >= expected_chunks:
            print("✅ 切分功能正常")
            return True
        else:
            print(f"❌ 切分异常：期望至少 {expected_chunks} 个节点，实际得到 {len(nodes)} 个")
            return False
            
    except Exception as e:
        print(f"❌ Word切分测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_actual_document_chunking():
    """测试实际文档的切分情况"""
    print("\n📂 测试实际文档切分...")
    
    try:
        from src.indices.index import load_nodes_from_disk
        from src.node_parser.node_parser_tool import get_parser_for_document
        
        # 加载实际文档
        docs = load_nodes_from_disk()
        if not docs:
            print("❌ 没有找到实际文档")
            return False
        
        print(f"📋 找到 {len(docs)} 个原始文档")
        
        for i, doc in enumerate(docs):
            print(f"\n📄 文档 {i+1}:")
            print(f"   ID: {doc.id_}")
            print(f"   长度: {len(doc.get_content())} 字符")
            
            # 检查元数据
            if hasattr(doc, 'metadata') and doc.metadata:
                file_name = doc.metadata.get('file_name', 'Unknown')
                print(f"   文件名: {file_name}")
                
                # 获取对应的解析器
                parser = get_parser_for_document(doc)
                print(f"   解析器类型: {type(parser).__name__}")
                print(f"   chunk_size: {getattr(parser, 'chunk_size', 'N/A')}")
                print(f"   chunk_overlap: {getattr(parser, 'chunk_overlap', 'N/A')}")
                
                # 尝试重新切分
                try:
                    nodes = parser.get_nodes_from_documents([doc])
                    print(f"   重新切分结果: {len(nodes)} 个节点")
                    
                    # 显示前3个节点的长度
                    for j, node in enumerate(nodes[:3]):
                        content_length = len(node.get_content())
                        print(f"      节点 {j+1}: {content_length} 字符")
                        
                except Exception as parse_error:
                    print(f"   ❌ 切分失败: {parse_error}")
        
        return True
        
    except Exception as e:
        print(f"❌ 实际文档测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_simple_node_parser_directly():
    """直接测试SimpleNodeParser的基础功能"""
    print("\n🔧 测试SimpleNodeParser基础功能...")
    
    try:
        from llama_index.core.node_parser import SimpleNodeParser
        from llama_index.core.schema import Document
        
        # 创建长文本
        long_text = "这是测试段落。" * 1000  # 约8000字符
        
        # 创建文档
        doc = Document(text=long_text)
        
        # 创建SimpleNodeParser
        parser = SimpleNodeParser(
            chunk_size=1200,
            chunk_overlap=150
        )
        
        print(f"📋 测试参数:")
        print(f"   文档长度: {len(long_text)} 字符")
        print(f"   chunk_size: {parser.chunk_size}")
        print(f"   chunk_overlap: {parser.chunk_overlap}")
        
        # 执行切分
        nodes = parser.get_nodes_from_documents([doc])
        
        print(f"\n📊 切分结果:")
        print(f"   生成节点数: {len(nodes)}")
        
        for i, node in enumerate(nodes[:5]):  # 只显示前5个
            content_length = len(node.get_content())
            print(f"   节点 {i+1}: {content_length} 字符")
        
        # 验证
        expected_nodes = len(long_text) // 1200 + 1
        if len(nodes) >= expected_nodes // 2:  # 允许一定误差
            print("✅ SimpleNodeParser基础功能正常")
            return True
        else:
            print(f"❌ 切分结果异常")
            return False
            
    except Exception as e:
        print(f"❌ SimpleNodeParser测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 开始Word文档切分功能排查")
    print("="*60)
    
    # 激活conda环境提示
    print("⚠️ 请确保已激活 llamaindex 环境：conda activate llamaindex")
    print()
    
    success_count = 0
    total_tests = 4
    
    # 测试1：配置检查
    if test_word_parser_configuration():
        success_count += 1
    
    # 测试2：模拟文档切分
    if test_word_chunking_with_mock_document():
        success_count += 1
    
    # 测试3：实际文档切分
    if test_actual_document_chunking():
        success_count += 1
    
    # 测试4：SimpleNodeParser基础功能
    if test_simple_node_parser_directly():
        success_count += 1
    
    print(f"\n📊 测试结果总结:")
    print(f"   成功: {success_count}/{total_tests}")
    print(f"   失败: {total_tests - success_count}/{total_tests}")
    
    if success_count == total_tests:
        print("🎉 所有测试通过！Word切分功能正常！")
    else:
        print("⚠️ 部分测试失败，Word切分功能存在问题") 