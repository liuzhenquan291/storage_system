"""
统一响应模型
"""
from typing import Any, Optional, List, Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class ResponseModel(BaseModel, Generic[T]):
    """统一响应模型"""
    code: int = Field(default=200, description="状态码")
    message: str = Field(default="操作成功", description="消息")
    data: Optional[T] = Field(default=None, description="数据")
    timestamp: int = Field(default=0, description="时间戳")
    
    class Config:
        json_schema_extra = {
            "example": {
                "code": 200,
                "message": "操作成功",
                "data": {},
                "timestamp": 1700000000000
            }
        }


class PagedData(BaseModel, Generic[T]):
    """分页数据模型"""
    list: List[T] = Field(default_factory=list, description="数据列表")
    total: int = Field(default=0, description="总数")
    page: int = Field(default=1, description="当前页")
    page_size: int = Field(default=20, description="每页大小")


class PagedResponseModel(BaseModel, Generic[T]):
    """分页响应模型"""
    code: int = Field(default=200, description="状态码")
    message: str = Field(default="查询成功", description="消息")
    data: PagedData[T] = Field(default_factory=PagedData, description="分页数据")
    timestamp: int = Field(default=0, description="时间戳")


def success_response(data: Any = None, message: str = "操作成功") -> dict:
    """成功响应"""
    import time
    return {
        "code": 200,
        "message": message,
        "data": data,
        "timestamp": int(time.time() * 1000)
    }


def error_response(message: str = "操作失败", code: int = 400, data: Any = None) -> dict:
    """错误响应"""
    import time
    return {
        "code": code,
        "message": message,
        "data": data,
        "timestamp": int(time.time() * 1000)
    }
