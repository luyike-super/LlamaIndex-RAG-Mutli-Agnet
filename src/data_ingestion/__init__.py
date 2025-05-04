"""
数据导入模块
"""

from .reader import default_reader
from .ingestion_pipeline import run_ingestion_pipeline

__all__ = ["default_reader","run_ingestion_pipeline"] 