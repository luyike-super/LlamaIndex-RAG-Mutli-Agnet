from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException
from app.models.response import ApiResponse, ResponseCode
import traceback
from typing import Union, Dict, Any


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """HTTP异常处理器"""
    # 映射HTTP状态码到响应码
    status_code_map = {
        400: ResponseCode.BAD_REQUEST,
        401: ResponseCode.UNAUTHORIZED,
        403: ResponseCode.FORBIDDEN,
        404: ResponseCode.NOT_FOUND,
        500: ResponseCode.INTERNAL_ERROR,
        503: ResponseCode.SERVICE_UNAVAILABLE
    }
    
    # 获取响应码
    response_code = status_code_map.get(exc.status_code, ResponseCode.UNKNOWN_ERROR)
    
    # 构建响应
    response = ApiResponse.error(
        code=response_code,
        message=str(exc.detail),
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=response.dict()
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """请求参数验证异常处理器"""
    # 格式化错误信息
    error_details = []
    for error in exc.errors():
        error_details.append({
            "loc": " -> ".join([str(loc) for loc in error["loc"]]),
            "msg": error["msg"],
            "type": error["type"]
        })
    
    # 构建响应
    response = ApiResponse.bad_request(
        message="请求参数验证失败",
        data=error_details
    )
    
    return JSONResponse(
        status_code=400,
        content=response.dict()
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """通用异常处理器"""
    # 记录错误详情（生产环境中这里应该记录到日志而不是返回给客户端）
    error_detail = {
        "exception": str(exc),
        "traceback": traceback.format_exc()
    }
    
    # 构建响应
    response = ApiResponse.server_error(
        message="服务器内部错误"
    )
    
    return JSONResponse(
        status_code=500,
        content=response.dict()
    )


def register_exception_handlers(app: FastAPI) -> None:
    """注册全局异常处理器"""
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler) 