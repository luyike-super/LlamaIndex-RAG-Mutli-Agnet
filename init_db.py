import asyncio
import os
from tortoise import Tortoise
from app.core.database import TORTOISE_ORM

async def init():
    """初始化数据库和迁移"""
    # 初始化数据库连接
    await Tortoise.init(config=TORTOISE_ORM)
    
    # 生成数据库表结构
    await Tortoise.generate_schemas()
    
    # 关闭连接
    await Tortoise.close_connections()
    
    print("数据库初始化完成！")

if __name__ == "__main__":
    asyncio.run(init()) 