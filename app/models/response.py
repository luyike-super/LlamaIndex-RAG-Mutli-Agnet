from typing import Generic, TypeVar, Optional, Any, Dict, List
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

# 定义泛型类型变量
T = TypeVar('T')

class ResponseCode(str, Enum):
    """响应状态码枚举"""
    SUCCESS = "200"           # 成功
    BAD_REQUEST = "400"       # 请求错误
    UNAUTHORIZED = "401"      # 未授权
    FORBIDDEN = "403"         # 禁止访问
    NOT_FOUND = "404"         # 资源不存在
    INTERNAL_ERROR = "500"    # 服务器内部错误
    SERVICE_UNAVAILABLE = "503"  # 服务不可用
    UNKNOWN_ERROR = "999"     # 未知错误


class ApiResponse(BaseModel, Generic[T]):
    """统一API响应结果"""
    code: str = Field(ResponseCode.SUCCESS, description="响应代码")
    message: str = Field("操作成功", description="响应消息")
    data: Optional[T] = Field(None, description="响应数据")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="响应时间戳")
    
    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )
    
    @classmethod
    def success(cls, data: Optional[T] = None, message: str = "操作成功") -> "ApiResponse[T]":
        """成功响应"""
        return cls(
            code=ResponseCode.SUCCESS,
            message=message,
            data=data,
            timestamp=datetime.now().isoformat()
        )
    
    @classmethod
    def error(cls, 
              code: str = ResponseCode.INTERNAL_ERROR, 
              message: str = "系统错误", 
              data: Optional[T] = None) -> "ApiResponse[T]":
        """错误响应"""
        return cls(
            code=code,
            message=message,
            data=data,
            timestamp=datetime.now().isoformat()
        )
    
    @classmethod
    def bad_request(cls, message: str = "请求参数错误", data: Optional[T] = None) -> "ApiResponse[T]":
        """请求参数错误"""
        return cls(
            code=ResponseCode.BAD_REQUEST,
            message=message,
            data=data,
            timestamp=datetime.now().isoformat()
        )
    
    @classmethod
    def unauthorized(cls, message: str = "未授权访问", data: Optional[T] = None) -> "ApiResponse[T]":
        """未授权错误"""
        return cls(
            code=ResponseCode.UNAUTHORIZED,
            message=message,
            data=data,
            timestamp=datetime.now().isoformat()
        )
    
    @classmethod
    def forbidden(cls, message: str = "禁止访问", data: Optional[T] = None) -> "ApiResponse[T]":
        """禁止访问错误"""
        return cls(
            code=ResponseCode.FORBIDDEN,
            message=message,
            data=data,
            timestamp=datetime.now().isoformat()
        )
    
    @classmethod
    def not_found(cls, message: str = "资源不存在", data: Optional[T] = None) -> "ApiResponse[T]":
        """资源不存在错误"""
        return cls(
            code=ResponseCode.NOT_FOUND,
            message=message,
            data=data,
            timestamp=datetime.now().isoformat()
        )
    
    @classmethod
    def server_error(cls, message: str = "服务器内部错误", data: Optional[T] = None) -> "ApiResponse[T]":
        """服务器内部错误"""
        return cls(
            code=ResponseCode.INTERNAL_ERROR,
            message=message,
            data=data,
            timestamp=datetime.now().isoformat()
        )


# 定义分页结果类型
class PageResult(BaseModel, Generic[T]):
    """分页结果"""
    items: List[T] = Field(default_factory=list, description="分页项目")
    total: int = Field(0, description="总记录数")
    page: int = Field(1, description="当前页码")
    size: int = Field(10, description="每页大小")
    pages: int = Field(0, description="总页数")
    has_next: bool = Field(False, description="是否有下一页")
    has_prev: bool = Field(False, description="是否有上一页")
    
    @classmethod
    def of(cls, items: List[T], total: int, page: int, size: int) -> "PageResult[T]":
        """创建分页结果"""
        pages = (total + size - 1) // size if size > 0 else 0
        return cls(
            items=items,
            total=total,
            page=page,
            size=size,
            pages=pages,
            has_next=page < pages,
            has_prev=page > 1
        ) 