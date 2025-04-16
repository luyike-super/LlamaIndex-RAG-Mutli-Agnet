from typing import Callable, Any
from fastapi import FastAPI, Request, Response
from fastapi.routing import APIRoute
from fastapi.responses import JSONResponse
import inspect
from starlette.background import BackgroundTask
from app.models.response import ApiResponse


class ResponseWrapperMiddleware:
    """
    响应包装中间件：自动将API响应包装为统一格式
    """
    
    def __init__(self, app: FastAPI):
        self.app = app
    
    async def __call__(self, request: Request, call_next: Callable) -> Response:
        # 调用下一个中间件或路由处理函数
        response = await call_next(request)
        
        # 检查请求路径是否应该被包装
        path = request.url.path
        
        # 跳过非API路径、OpenAPI文档等路径的包装
        if not path.startswith("/api") or path.endswith(("/docs", "/redoc", "/openapi.json")):
            return response
        
        # 如果已经是JSONResponse且状态码为200，尝试包装响应
        if isinstance(response, JSONResponse) and response.status_code == 200:
            # 尝试获取响应体
            try:
                response_body = response.body.decode("utf-8")
                
                # 检查是否已经是ApiResponse格式
                import json
                response_data = json.loads(response_body)
                
                # 如果已经有code和message字段，说明已经是统一响应格式，不再包装
                if isinstance(response_data, dict) and "code" in response_data and "message" in response_data:
                    return response
                
                # 否则，包装为ApiResponse
                wrapped_response = ApiResponse.success(data=response_data).dict()
                return JSONResponse(
                    content=wrapped_response,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    background=getattr(response, "background", None)
                )
            except Exception:
                # 解析失败，返回原始响应
                pass
        
        # 返回原始响应
        return response


def register_response_middleware(app: FastAPI) -> None:
    """注册响应包装中间件"""
    app.add_middleware(ResponseWrapperMiddleware) 