#!/usr/bin/env python3
import os
import sys
import argparse
import uvicorn
from dotenv import load_dotenv

def main():
    parser = argparse.ArgumentParser(description="LlamaKB 服务启动脚本")
    parser.add_argument(
        "--host", 
        type=str, 
        default="0.0.0.0", 
        help="服务主机地址"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=8000, 
        help="服务端口"
    )
    parser.add_argument(
        "--reload", 
        action="store_true", 
        help="是否自动重载"
    )
    
    args = parser.parse_args()
    
    # 加载.env配置文件
    if os.path.exists(".env"):
        print("加载环境配置: .env")
        load_dotenv()
    
    # 获取调试模式设置
    debug_mode = os.getenv("DEBUG", "true").lower() == "true"
    
    # 启动服务
    print(f"启动服务: 主机={args.host}, 端口={args.port}, 自动重载={args.reload}")
    
    uvicorn.run(
        "app.main:app", 
        host=args.host, 
        port=args.port, 
        reload=args.reload,
        log_level="debug" if debug_mode else "info"
    )

if __name__ == "__main__":
    main() 