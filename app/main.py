from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router
from app.core.config import settings
from app.middlewares.response_wrapper import register_response_middleware
from app.middlewares.exception_handler import register_exception_handlers
# 暂时注释掉Tortoise导入
# from app.core.database import init_db, close_db

# 创建应用
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    debug=settings.DEBUG
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOW_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# 注册统一响应中间件
register_response_middleware(app)

# 注册异常处理器
register_exception_handlers(app)

# 注册路由
app.include_router(api_router, prefix=settings.API_V1_STR)

# 暂时注释掉数据库初始化代码
# @app.on_event("startup")
# async def startup_db():
#     await init_db()

# @app.on_event("shutdown")
# async def shutdown_db():
#     await close_db()

@app.get("/")
async def root():
    return {
        "message": "欢迎使用LlamaKB API服务",
        "version": settings.VERSION
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 