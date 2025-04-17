import os
from typing import Optional, List, Dict, Any
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class AppSettings(BaseSettings):
    """应用配置"""
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "LlamaKB")
    PROJECT_DESCRIPTION: str = os.getenv("PROJECT_DESCRIPTION", "基于LlamaIndex和FastAPI的RAG应用")
    VERSION: str = os.getenv("VERSION", "0.1.0")
    
    # 调试设置
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    # OpenAI配置
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # DeepSeek配置
    DEEPSEEK_API_KEY: Optional[str] = os.getenv("DEEPSEEK_API_KEY")
    DEEPSEEK_API_BASE: Optional[str] = os.getenv("DEEPSEEK_API_BASE")
    DEEPSEEK_MODEL: Optional[str] = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    
    # DashScope配置
    DASHSCOPE_API_KEY: Optional[str] = os.getenv("DASHSCOPE_API_KEY")
    DASHSCOPE_API_BASE: Optional[str] = os.getenv("DASHSCOPE_API_BASE")
    
    # 数据存储路径
    DATA_DIR: str = os.getenv("DATA_DIR", "data")
    INDEX_DIR: str = os.getenv("INDEX_DIR", "index")
    
    # 数据库配置
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "postgres")
    DB_NAME: str = os.getenv("DB_NAME", "llamakb")
    
    # CORS配置 - 允许所有跨域请求
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]
    CORS_ALLOW_ORIGINS: List[str] = ["*"]
    
    # 超时设置
    OPENAI_TIMEOUT: int = int(os.getenv("OPENAI_TIMEOUT", "60"))
    DEEPSEEK_TIMEOUT: int = int(os.getenv("DEEPSEEK_TIMEOUT", "60"))
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

# 创建单一设置实例
settings = AppSettings() 