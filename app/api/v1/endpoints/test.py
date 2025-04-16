from fastapi import APIRouter, Depends
from app.core.config import ENV
from app.models.response import ApiResponse
from pydantic import BaseModel
from fastapi import Form

class item(BaseModel) :
    name : str
    age : int


router = APIRouter()


@router.post("/")
async def test_endpoint(name: str = Form(...), age: int = Form(...)):
    """测试端点"""
    return ApiResponse.success(
        data={
            "status": "ok",
            "environment": ENV,
            "message": name
        },
        message="222"
    )

@router.get("/error")
async def test_error() -> ApiResponse[None]:
    """测试错误响应"""
    return ApiResponse.error(
        message="这是一个模拟的错误响应"
    ) 