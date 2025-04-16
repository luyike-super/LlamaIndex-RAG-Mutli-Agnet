import os
from typing import List, Dict, Any
import json
from pathlib import Path


def ensure_dir(directory: str) -> str:
    """确保目录存在，如果不存在则创建"""
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    return str(path)


def save_json(data: Dict[str, Any], file_path: str) -> None:
    """保存数据为JSON文件"""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_json(file_path: str) -> Dict[str, Any]:
    """从JSON文件加载数据"""
    if not os.path.exists(file_path):
        return {}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def list_files(directory: str, extensions: List[str] = None) -> List[str]:
    """列出目录中的所有文件，可选择按扩展名过滤"""
    if not os.path.exists(directory):
        return []
    
    files = []
    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            if extensions is None or any(filename.endswith(ext) for ext in extensions):
                files.append(os.path.join(root, filename))
    
    return files 