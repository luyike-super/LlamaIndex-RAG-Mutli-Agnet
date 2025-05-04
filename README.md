# LlamaKB - 基于LlamaIndex的知识库系统

## 项目介绍

LlamaKB是一个基于LlamaIndex构建的知识库系统，支持文档导入、处理、索引和查询。系统可以处理多种文档格式，自动提取内容摘要，并针对不同类别的文档构建专门的查询引擎。

## 主要功能

- 文档导入：支持多种格式（Markdown、Word等）文档的导入和处理
- 文档转换：自动清洗数据、提取摘要、分类和URL规范化
- 知识索引：基于向量存储建立文档索引，支持语义搜索
- 查询引擎：为每个文档或文档类别构建专门的查询引擎
- 智能代理：使用ReAct代理模式实现更智能的多文档交互式问答
- workflow:  多智能体工作流，保证检索和回答质量
## 项目结构

```
LlamaKB/
├── app/              # 应用程序目录
│   └── api/          # API接口
├── config/           # 配置文件
├── data/             # 数据文件目录
├── logs/             # 日志文件目录
├── notebooks/        # Jupyter笔记本
├── scripts/          # 脚本文件
├── src/              # 源代码
│   ├── agent/        # 智能代理实现
│   ├── data_ingestion/  # 数据导入模块
│   ├── indices/      # 索引模块
│   ├── models/       # 模型工厂和接口
│   ├── NodeParser/   # 节点解析器
│   ├── query_engine/ # 查询引擎
│   ├── transformations/ # 数据转换器
│   └── utils/        # 工具函数
└── tests/            # 测试文件
```

## 环境要求

- Python 3.8+
- 依赖包见requirements.txt（如有）

## 安装步骤

1. 克隆仓库
   ```bash
   git clone https://github.com/yourusername/LlamaKB.git
   cd LlamaKB
   ```

2. 安装依赖
   ```bash
   pip install -r requirements.txt
   ```

3. 配置环境变量
   创建`.env`文件配置API密钥等必要参数

## 使用方法

### 数据导入

将文档放置在`data/`目录下，系统会自动识别和处理。

### 运行测试

```bash
python tests/test_ingestion_pipeline.py
```

### 查询示例

```python
from src.indices.index import test_load_docs

# 获取文档查询引擎字典
doc_engines = test_load_docs()

# 执行查询
response = doc_engines["document_id"].query("您的问题")
print(response)
```

## 模型支持

本项目支持多种大语言模型和嵌入模型：

- LLM提供商：千问、星火、通义、DeepSeek等
- 嵌入模型：DashScope、OpenAI等

## 贡献指南

欢迎提交Issues和Pull Requests。

## 许可证

[添加您的许可证信息] 