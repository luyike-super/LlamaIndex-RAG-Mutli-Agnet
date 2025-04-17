import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logger():
    """配置并返回 LlamaIndex 项目的日志记录器"""
    # 创建记录器
    logger = logging.getLogger('LlamaIndex')
    logger.setLevel(logging.INFO)
    
    # 如果已经配置过处理器，直接返回
    if logger.handlers:
        return logger
    
    # 确保日志目录存在
    log_dir = "./logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # 创建文件处理器（使用轮转文件处理器）
    file_handler = RotatingFileHandler(
        filename=os.path.join(log_dir, 'llamaindex.log'),
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    
    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 设置处理器的格式化器
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    # 添加处理器到记录器
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

# 创建全局日志记录器
logger = setup_logger() 