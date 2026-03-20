"""
用户相关 Schema
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class UserLogin(BaseModel):
    """用户登录"""
    username: str = Field(..., description="用户名", min_length=2, max_length=50)
    password: str = Field(..., description="密码", min_length=6, max_length=50)


class UserCreate(BaseModel):
    """创建用户"""
    username: str = Field(..., description="用户名", min_length=2, max_length=50)
    password: str = Field(..., description="密码", min_length=6, max_length=50)
    real_name: str = Field(..., description="真实姓名", min_length=2, max_length=50)
    role_id: Optional[int] = Field(None, description="角色ID")
    warehouse_id: Optional[int] = Field(None, description="所属库房ID")
    phone: Optional[str] = Field(None, description="联系电话", max_length=20)
    email: Optional[str] = Field(None, description="邮箱", max_length=100)


class UserUpdate(BaseModel):
    """更新用户"""
    real_name: Optional[str] = Field(None, description="真实姓名", max_length=50)
    role_id: Optional[int] = Field(None, description="角色ID")
    warehouse_id: Optional[int] = Field(None, description="所属库房ID")
    phone: Optional[str] = Field(None, description="联系电话", max_length=20)
    email: Optional[str] = Field(None, description="邮箱", max_length=100)
    status: Optional[int] = Field(None, description="状态")


class UserResponse(BaseModel):
    """用户响应"""
    id: int
    username: str
    real_name: str
    role_id: Optional[int] = None
    warehouse_id: Optional[int] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    status: int
    created_time: Optional[str] = None
    updated_time: Optional[str] = None


class TokenResponse(BaseModel):
    """Token响应"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
