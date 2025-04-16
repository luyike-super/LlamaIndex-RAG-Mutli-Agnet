from tortoise import Tortoise
from app.core.config import settings

# 数据库URL
DATABASE_URL = f"postgres://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"

# Tortoise ORM配置
TORTOISE_ORM = {
    "connections": {"default": DATABASE_URL},
    "apps": {
        "models": {
            "models": ["app.models.models", "aerich.models"],
            "default_connection": "default",
        },
    },
    "use_tz": False,
    "timezone": "Asia/Shanghai"
}

async def init_db():
    """初始化数据库连接"""
    await Tortoise.init(
        db_url=DATABASE_URL,
        modules={"models": ["app.models.models"]}
    )
    # 如果需要生成表结构
    await Tortoise.generate_schemas()

async def close_db():
    """关闭数据库连接"""
    await Tortoise.close_connections() 