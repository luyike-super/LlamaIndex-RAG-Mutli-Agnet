"""
检索效果评估工具
"""
import time
import logging
from typing import List, Dict, Any, Tuple
from llama_index.core.schema import NodeWithScore
from config.config_rag import RETRIEVAL_CONFIG

logger = logging.getLogger(__name__)

class RetrievalEvaluator:
    """检索效果评估工具"""
    
    def __init__(self):
        self.evaluation_results = []
    
    def evaluate_query(
        self, 
        query: str, 
        query_engine: Any,
        expected_keywords: List[str] = None,
        expected_docs: List[str] = None
    ) -> Dict[str, Any]:
        """
        评估单个查询的检索效果
        
        Args:
            query: 查询字符串
            query_engine: 查询引擎
            expected_keywords: 期望在结果中出现的关键词
            expected_docs: 期望检索到的文档ID
            
        Returns:
            评估结果字典
        """
        start_time = time.time()
        
        try:
            # 执行查询
            response = query_engine.query(query)
            query_time = time.time() - start_time
            
            # 提取检索到的节点
            retrieved_nodes = getattr(response, 'source_nodes', [])
            
            # 计算评估指标
            metrics = self._calculate_metrics(
                query=query,
                retrieved_nodes=retrieved_nodes,
                response_text=str(response),
                expected_keywords=expected_keywords,
                expected_docs=expected_docs,
                query_time=query_time
            )
            
            # 保存评估结果
            evaluation_result = {
                "query": query,
                "response": str(response),
                "metrics": metrics,
                "retrieved_count": len(retrieved_nodes),
                "query_time": query_time,
                "timestamp": time.time()
            }
            
            self.evaluation_results.append(evaluation_result)
            
            return evaluation_result
            
        except Exception as e:
            logger.error(f"评估查询 '{query}' 时出错: {e}")
            return {
                "query": query,
                "error": str(e),
                "query_time": time.time() - start_time
            }
    
    def _calculate_metrics(
        self,
        query: str,
        retrieved_nodes: List[NodeWithScore],
        response_text: str,
        expected_keywords: List[str] = None,
        expected_docs: List[str] = None,
        query_time: float = 0
    ) -> Dict[str, float]:
        """计算检索评估指标"""
        
        metrics = {
            "retrieval_count": len(retrieved_nodes),
            "avg_score": 0.0,
            "min_score": 0.0,
            "max_score": 0.0,
            "keyword_coverage": 0.0,
            "doc_recall": 0.0,
            "response_length": len(response_text),
            "query_time": query_time
        }
        
        if not retrieved_nodes:
            return metrics
        
        # 计算分数统计
        scores = [node.score for node in retrieved_nodes if node.score is not None]
        if scores:
            metrics["avg_score"] = sum(scores) / len(scores)
            metrics["min_score"] = min(scores)
            metrics["max_score"] = max(scores)
        
        # 计算关键词覆盖率
        if expected_keywords:
            metrics["keyword_coverage"] = self._calculate_keyword_coverage(
                response_text, expected_keywords
            )
        
        # 计算文档召回率
        if expected_docs:
            metrics["doc_recall"] = self._calculate_doc_recall(
                retrieved_nodes, expected_docs
            )
        
        return metrics
    
    def _calculate_keyword_coverage(
        self, 
        response_text: str, 
        expected_keywords: List[str]
    ) -> float:
        """计算关键词覆盖率"""
        if not expected_keywords:
            return 0.0
        
        response_lower = response_text.lower()
        found_keywords = 0
        
        for keyword in expected_keywords:
            if keyword.lower() in response_lower:
                found_keywords += 1
        
        return found_keywords / len(expected_keywords)
    
    def _calculate_doc_recall(
        self, 
        retrieved_nodes: List[NodeWithScore], 
        expected_docs: List[str]
    ) -> float:
        """计算文档召回率"""
        if not expected_docs:
            return 0.0
        
        retrieved_doc_ids = set()
        for node in retrieved_nodes:
            if hasattr(node.node, 'ref_doc_id') and node.node.ref_doc_id:
                retrieved_doc_ids.add(node.node.ref_doc_id)
        
        found_docs = len(retrieved_doc_ids.intersection(set(expected_docs)))
        return found_docs / len(expected_docs)
    
    def run_evaluation_suite(
        self, 
        test_queries: List[Dict[str, Any]], 
        query_engine: Any
    ) -> Dict[str, Any]:
        """
        运行评估测试套件
        
        Args:
            test_queries: 测试查询列表，每个包含query、expected_keywords等
            query_engine: 要评估的查询引擎
            
        Returns:
            综合评估结果
        """
        logger.info(f"开始运行评估套件，共 {len(test_queries)} 个测试查询")
        
        results = []
        for test_case in test_queries:
            query = test_case["query"]
            expected_keywords = test_case.get("expected_keywords", [])
            expected_docs = test_case.get("expected_docs", [])
            
            result = self.evaluate_query(
                query=query,
                query_engine=query_engine,
                expected_keywords=expected_keywords,
                expected_docs=expected_docs
            )
            results.append(result)
        
        # 计算综合指标
        summary = self._calculate_summary_metrics(results)
        
        logger.info("评估套件运行完成")
        
        return {
            "individual_results": results,
            "summary": summary,
            "total_queries": len(test_queries),
            "successful_queries": len([r for r in results if "error" not in r])
        }
    
    def _calculate_summary_metrics(self, results: List[Dict[str, Any]]) -> Dict[str, float]:
        """计算综合评估指标"""
        valid_results = [r for r in results if "error" not in r and "metrics" in r]
        
        if not valid_results:
            return {}
        
        # 提取所有指标
        all_metrics = [r["metrics"] for r in valid_results]
        
        summary = {}
        metric_names = [
            "retrieval_count", "avg_score", "keyword_coverage", 
            "doc_recall", "response_length", "query_time"
        ]
        
        for metric_name in metric_names:
            values = [m.get(metric_name, 0) for m in all_metrics]
            if values:
                summary[f"avg_{metric_name}"] = sum(values) / len(values)
                summary[f"max_{metric_name}"] = max(values)
                summary[f"min_{metric_name}"] = min(values)
        
        return summary
    
    def print_evaluation_report(self, evaluation_result: Dict[str, Any]):
        """打印评估报告"""
        print("\n" + "="*50)
        print("检索效果评估报告")
        print("="*50)
        
        if "summary" in evaluation_result:
            print("\n📊 综合指标:")
            summary = evaluation_result["summary"]
            
            print(f"  • 平均检索数量: {summary.get('avg_retrieval_count', 0):.1f}")
            print(f"  • 平均相似度分数: {summary.get('avg_avg_score', 0):.3f}")
            print(f"  • 平均关键词覆盖率: {summary.get('avg_keyword_coverage', 0)*100:.1f}%")
            print(f"  • 平均文档召回率: {summary.get('avg_doc_recall', 0)*100:.1f}%")
            print(f"  • 平均响应长度: {summary.get('avg_response_length', 0):.0f} 字符")
            print(f"  • 平均查询时间: {summary.get('avg_query_time', 0):.2f} 秒")
        
        print(f"\n📈 总体统计:")
        print(f"  • 总查询数: {evaluation_result.get('total_queries', 0)}")
        print(f"  • 成功查询数: {evaluation_result.get('successful_queries', 0)}")
        
        # 打印个别查询结果
        if "individual_results" in evaluation_result:
            print(f"\n📝 详细结果:")
            for i, result in enumerate(evaluation_result["individual_results"][:5], 1):
                if "error" not in result:
                    metrics = result.get("metrics", {})
                    print(f"  {i}. 查询: {result['query'][:50]}...")
                    print(f"     检索数量: {metrics.get('retrieval_count', 0)}")
                    print(f"     平均分数: {metrics.get('avg_score', 0):.3f}")
                    print(f"     查询时间: {metrics.get('query_time', 0):.2f}s")

def create_test_queries() -> List[Dict[str, Any]]:
    """创建测试查询集合"""
    return [
        {
            "query": "使用硬件控制模式，输出类型设置为 HCSL",
            "expected_keywords": ["硬件控制", "HCSL", "输出类型", "driver_type", "output_drive_low"],
            "description": "硬件控制和输出类型配置"
        },
        {
            "query": "时钟输出频率如何配置",
            "expected_keywords": ["时钟", "频率", "配置", "输出", "clock"],
            "description": "时钟频率配置"
        },
        {
            "query": "芯片的供电电压范围",
            "expected_keywords": ["供电", "电压", "范围", "芯片", "VDD"],
            "description": "供电电压规格"
        },
        {
            "query": "SPI接口如何使用",
            "expected_keywords": ["SPI", "接口", "使用", "通信", "配置"],
            "description": "SPI接口使用方法"
        },
        {
            "query": "温度范围和工作条件",
            "expected_keywords": ["温度", "范围", "工作条件", "环境", "规格"],
            "description": "工作环境规格"
        }
    ] 