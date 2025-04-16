# LlamaKB

基于LlamaIndex和FastAPI构建的RAG（检索增强生成）知识库系统。

## 功能特点

- 基于LlamaIndex提供高效的文档检索
- 使用OpenAI API生成高质量回答
- RESTful API接口，易于集成
- 支持多种文档格式
- 多环境配置支持（开发、测试、生产）
- 可配置的CORS跨域资源共享

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置环境变量

项目支持多环境配置，包括开发环境(development)、测试环境(testing)和生产环境(production)。

```bash
# 复制环境变量示例文件
cp .env.example .env

# 或直接使用特定环境的配置
cp .env.development .env   # 开发环境
cp .env.testing .env       # 测试环境
cp .env.production .env    # 生产环境
```

编辑`.env`文件，填入您的OpenAI API密钥和其他配置。

### 启动服务

使用启动脚本在不同环境中启动应用：

```bash
# 开发环境启动（默认）
python run.py

# 测试环境启动
python run.py --env testing

# 生产环境启动
python run.py --env production --host 0.0.0.0 --port 8000
```

或直接使用uvicorn:

```bash
# 开发环境
ENVIRONMENT=development uvicorn app.main:app --reload

# 生产环境
ENVIRONMENT=production uvicorn app.main:app
```

服务将在 http://localhost:8000 上启动，您可以访问 http://localhost:8000/api/v1/docs 查看API文档。

## 跨域资源共享(CORS)配置

各环境的CORS配置如下：

- **开发环境**: 允许所有来源请求
- **测试环境**: 允许特定域名请求 (localhost和test.llamakb.com)
- **生产环境**: 严格限制，只允许特定域名请求

您可以在`app/core/config.py`中修改CORS配置。

## 项目结构

```
app/
├── api/                # API定义
│   └── v1/             # API版本1
│       └── endpoints/  # API端点
├── core/               # 核心配置
├── models/             # 数据模型
├── services/           # 业务逻辑
└── utils/              # 工具函数
```

## API文档

启动服务后，访问 http://localhost:8000/api/v1/docs 查看Swagger文档。
