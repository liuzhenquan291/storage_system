"""
认证相关 API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.response import success_response, error_response
from app.schemas.user import UserLogin, TokenResponse
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/login", summary="用户登录")
async def login(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """用户登录"""
    result = await AuthService.login(db, login_data)
    
    if not result:
        return error_response(message="用户名或密码错误", code=401)
    
    return success_response(data=result.model_dump(), message="登录成功")


@router.post("/logout", summary="用户登出")
async def logout():
    """用户登出"""
    return success_response(message="登出成功")
