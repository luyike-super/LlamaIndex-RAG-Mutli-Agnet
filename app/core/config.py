import os
from typing import Optional, List, Dict, Any, Union
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 获取当前环境
ENV = os.getenv("ENVIRONMENT", "development")


class BaseAppSettings(BaseSettings):
    """基础配置"""
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "LlamaKB"
    PROJECT_DESCRIPTION: str = "基于LlamaIndex和FastAPI的RAG应用"
    VERSION: str = "0.1.0"
    
    # OpenAI配置
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # 数据存储路径
    DATA_DIR: str = os.getenv("DATA_DIR", "data")
    INDEX_DIR: str = os.getenv("INDEX_DIR", "index")
    
    # CORS配置 - 基础设置
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


class DevelopmentSettings(BaseAppSettings):
    """开发环境配置"""
    DEBUG: bool = True
    
    # 开发环境允许所有跨域请求
    CORS_ALLOW_ORIGINS: List[str] = ["*"]


class TestingSettings(BaseAppSettings):
    """测试环境配置"""
    DEBUG: bool = True
    TESTING: bool = True
    
    # 测试环境允许特定域名
    CORS_ALLOW_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://test.llamakb.com",
    ]


class ProductionSettings(BaseAppSettings):
    """生产环境配置"""
    DEBUG: bool = False
    
    # 生产环境只允许特定域名
    CORS_ALLOW_ORIGINS: List[str] = [
        "https://llamakb.com",
        "https://api.llamakb.com",
        "https://admin.llamakb.com",
    ]
    
    # 生产环境其他配置
    OPENAI_TIMEOUT: int = 60


# 配置映射
environments: Dict[str, Any] = {
    "development": DevelopmentSettings,
    "testing": TestingSettings,
    "production": ProductionSettings,
}

# 根据环境变量加载对应的配置
settings: Union[DevelopmentSettings, TestingSettings, ProductionSettings] = environments[ENV]() 