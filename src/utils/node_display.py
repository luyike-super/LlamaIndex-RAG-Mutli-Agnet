"""
文档节点展示工具
"""
from typing import List, Dict, Any
from llama_index.core.schema import NodeWithScore
import json

class NodeDisplayer:
    """文档节点展示工具类"""
    
    def __init__(self, max_content_length: int = 200):
        self.max_content_length = max_content_length
    
    def display_nodes(self, nodes: List[NodeWithScore], query: str = "") -> None:
        """
        美观地显示检索到的节点
        
        Args:
            nodes: 检索到的节点列表
            query: 原始查询（用于高亮显示）
        """
        if not nodes:
            print("❌ 没有检索到任何文档节点")
            return
        
        print(f"\n🔍 查询: '{query}'")
        print(f"📄 检索到 {len(nodes)} 个相关文档节点\n")
        print("=" * 80)
        
        for i, node_with_score in enumerate(nodes, 1):
            self._display_single_node(i, node_with_score, query)
            print("-" * 80)
    
    def _display_single_node(self, index: int, node_with_score: NodeWithScore, query: str = "") -> None:
        """显示单个节点"""
        node = node_with_score.node
        score = node_with_score.score or 0.0
        
        print(f"📋 节点 {index}")
        print(f"   🎯 相似度分数: {score:.4f}")
        
        # 显示节点ID
        if hasattr(node, 'node_id') and node.node_id:
            print(f"   🆔 节点ID: {node.node_id}")
        
        # 显示文档ID（如果有）
        if hasattr(node, 'ref_doc_id') and node.ref_doc_id:
            print(f"   📚 文档ID: {node.ref_doc_id}")
        
        # 显示元数据
        if hasattr(node, 'metadata') and node.metadata:
            self._display_metadata(node.metadata)
        
        # 显示内容
        content = node.get_content() if hasattr(node, 'get_content') else str(node)
        self._display_content(content, query)
    
    def _display_metadata(self, metadata: Dict[str, Any]) -> None:
        """显示节点元数据"""
        if not metadata:
            return
        
        print(f"   📊 元数据:")
        for key, value in metadata.items():
            if key in ['file_name', 'category', 'summary', 'parser_type']:
                # 显示重要的元数据
                display_value = str(value)[:100] + "..." if len(str(value)) > 100 else str(value)
                print(f"      • {key}: {display_value}")
    
    def _display_content(self, content: str, query: str = "") -> None:
        """显示节点内容，可选高亮查询词"""
        if not content:
            print(f"   📝 内容: [空内容]")
            return
        
        # 截取内容
        if len(content) > self.max_content_length:
            display_content = content[:self.max_content_length] + "..."
        else:
            display_content = content
        
        # 简单的查询词高亮（如果提供了查询）
        if query:
            query_words = query.split()
            for word in query_words:
                if len(word) > 2:  # 只高亮长度大于2的词
                    display_content = display_content.replace(
                        word, f"【{word}】"
                    )
        
        print(f"   📝 内容: {display_content}")
        print(f"   📏 完整长度: {len(content)} 字符")
    
    def get_nodes_summary(self, nodes: List[NodeWithScore]) -> Dict[str, Any]:
        """
        获取节点的统计摘要
        
        Args:
            nodes: 节点列表
            
        Returns:
            Dict: 包含统计信息的字典
        """
        if not nodes:
            return {"total_nodes": 0}
        
        # 基本统计
        total_nodes = len(nodes)
        scores = [node.score for node in nodes if node.score is not None]
        
        summary = {
            "total_nodes": total_nodes,
            "avg_score": sum(scores) / len(scores) if scores else 0.0,
            "max_score": max(scores) if scores else 0.0,
            "min_score": min(scores) if scores else 0.0,
            "total_content_length": sum(len(node.node.get_content()) for node in nodes),
        }
        
        # 文档来源统计
        doc_sources = {}
        categories = {}
        parsers = {}
        
        for node in nodes:
            if hasattr(node.node, 'metadata') and node.node.metadata:
                metadata = node.node.metadata
                
                # 统计文档来源
                if 'file_name' in metadata:
                    file_name = metadata['file_name']
                    doc_sources[file_name] = doc_sources.get(file_name, 0) + 1
                
                # 统计类别
                if 'category' in metadata:
                    category = metadata['category']
                    categories[category] = categories.get(category, 0) + 1
                
                # 统计解析器类型
                if 'parser_type' in metadata:
                    parser = metadata['parser_type']
                    parsers[parser] = parsers.get(parser, 0) + 1
        
        summary.update({
            "doc_sources": doc_sources,
            "categories": categories,
            "parser_types": parsers
        })
        
        return summary
    
    def print_summary(self, nodes: List[NodeWithScore]) -> None:
        """打印节点统计摘要"""
        summary = self.get_nodes_summary(nodes)
        
        print("\n📊 检索节点统计摘要")
        print("=" * 50)
        print(f"📄 总节点数: {summary['total_nodes']}")
        
        if summary['total_nodes'] > 0:
            print(f"🎯 平均分数: {summary['avg_score']:.4f}")
            print(f"📏 总内容长度: {summary['total_content_length']} 字符")
            
            # 显示文档来源分布
            if summary['doc_sources']:
                print(f"\n📚 文档来源分布:")
                for doc, count in summary['doc_sources'].items():
                    print(f"   • {doc}: {count} 个节点")
            
            # 显示类别分布
            if summary['categories']:
                print(f"\n🏷️ 类别分布:")
                for category, count in summary['categories'].items():
                    short_category = category[:50] + "..." if len(category) > 50 else category
                    print(f"   • {short_category}: {count} 个节点")
            
            # 显示解析器类型分布
            if summary['parser_types']:
                print(f"\n🔧 解析器类型分布:")
                for parser, count in summary['parser_types'].items():
                    print(f"   • {parser}: {count} 个节点")

def display_retrieved_nodes(nodes: List[NodeWithScore], query: str = "", show_summary: bool = True) -> None:
    """
    便捷函数：显示检索到的节点
    
    Args:
        nodes: 检索到的节点列表
        query: 原始查询
        show_summary: 是否显示统计摘要
    """
    displayer = NodeDisplayer()
    
    if show_summary:
        displayer.print_summary(nodes)
    
    displayer.display_nodes(nodes, query)

def save_nodes_to_json(nodes: List[NodeWithScore], file_path: str) -> None:
    """
    将检索到的节点保存为JSON文件
    
    Args:
        nodes: 节点列表
        file_path: 保存路径
    """
    nodes_data = []
    
    for i, node_with_score in enumerate(nodes):
        node_data = {
            "index": i + 1,
            "score": node_with_score.score,
            "node_id": getattr(node_with_score.node, 'node_id', None),
            "doc_id": getattr(node_with_score.node, 'ref_doc_id', None),
            "metadata": getattr(node_with_score.node, 'metadata', {}),
            "content": node_with_score.node.get_content(),
            "content_length": len(node_with_score.node.get_content())
        }
        nodes_data.append(node_data)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(nodes_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 节点数据已保存到: {file_path}") 