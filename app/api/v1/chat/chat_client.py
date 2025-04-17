from typing import List, Dict, Any
from pydantic import BaseModel, ValidationError
from fastapi import Depends, Request, Body, HTTPException
from fastapi.routing import APIRouter
from app.models.llm.create_llm import client_qwen
from app.models.response import ApiResponse

router = APIRouter()

class ChatMessage(BaseModel):
    """聊天消息模型"""
    role: str
    content: str

class ChatRequest(BaseModel):
    """聊天请求模型"""
    messages: List[ChatMessage]

@router.post("")
async def chat(request: ChatRequest = Body(...)) -> ApiResponse:
    """处理聊天请求
    
    接收用户的聊天消息，并返回AI响应
    """
    try:
        # 获取用户消息
        if not request.messages or len(request.messages) == 0:
            return ApiResponse.bad_request(message="消息不能为空")
        
        # 获取最后一条用户消息
        user_message = request.messages[-1].content
        
        # 调用大模型
        try:
            response = client_qwen.complete(user_message)
            response_text = str(response).strip()
        except Exception as e:
            return ApiResponse.error(message=f"模型调用失败: {str(e)}")
        
        # 返回响应
        return ApiResponse.success(
            data={"message": response_text},
            message="聊天响应成功"
        )
        
    except Exception as e:
        # 捕获所有异常
        return ApiResponse.error(message=f"处理聊天请求失败: {str(e)}")
