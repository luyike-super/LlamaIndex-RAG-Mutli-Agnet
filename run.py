#!/usr/bin/env python3
import os
import sys
import argparse
import uvicorn

def main():
    parser = argparse.ArgumentParser(description="LlamaKB 服务启动脚本")
    parser.add_argument(
        "--env", 
        type=str, 
        default="development", 
        choices=["development", "testing", "production"],
        help="运行环境 (development/testing/production)"
    )
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
        help="是否自动重载（仅适用于开发环境）"
    )
    
    args = parser.parse_args()
    
    # 设置环境变量
    os.environ["ENVIRONMENT"] = args.env
    
    # 加载对应环境的配置文件
    env_file = f".env.{args.env}"
    if os.path.exists(env_file):
        print(f"加载环境配置: {env_file}")
        # dotenv只会在加载时覆盖尚未设置的环境变量，
        # 因此我们先手动设置ENVIRONMENT，确保它不会被覆盖
        from dotenv import load_dotenv
        load_dotenv(env_file)
    
    # 启动服务
    reload_option = args.reload and args.env != "production"
    print(f"启动服务: 环境={args.env}, 主机={args.host}, 端口={args.port}, 自动重载={reload_option}")
    
    uvicorn.run(
        "app.main:app", 
        host=args.host, 
        port=args.port, 
        reload=reload_option,
        log_level="info" if args.env == "production" else "debug"
    )

if __name__ == "__main__":
    main() 