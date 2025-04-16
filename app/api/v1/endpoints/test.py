from fastapi import APIRouter, Depends
from app.core.config import ENV
from app.models.response import ApiResponse
from typing import Dict, Any

router = APIRouter()

@router.get("/")
async def test_endpoint() -> ApiResponse[Dict[str, Any]]:
    """测试端点"""
    return ApiResponse.success(
        data={
            "status": "ok",
            "environment": ENV,
            "message": "测试API端点工作正常"
        },
        message="测试成功"
    )

@router.get("/error")
async def test_error() -> ApiResponse[None]:
    """测试错误响应"""
    return ApiResponse.error(
        message="这是一个模拟的错误响应"
    ) 