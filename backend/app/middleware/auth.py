"""
认证中间件和权限装饰器
"""
from typing import Optional, List
from functools import wraps
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db, AsyncSessionLocal
from app.core.security import decode_access_token
from app.core.config import settings
from app.models.sys_user import SysUser
from app.models.sys_role import SysRole
from app.models.sys_resource import SysResource, SysRoleResource
from loguru import logger


# HTTP Bearer 认证
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> SysUser:
    """获取当前用户"""
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭证"
        )
    
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭证"
        )
    
    result = await db.execute(
        select(SysUser).where(SysUser.id == user_id, SysUser.deleted == 0)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在"
        )
    
    if user.status != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用"
        )
    
    return user


async def get_user_permissions(db: AsyncSession, user: SysUser) -> List[str]:
    """获取用户的所有权限码"""
    # 获取用户角色
    result = await db.execute(
        select(SysRole).where(SysRole.id == user.role_id, SysRole.deleted == 0)
    )
    role = result.scalar_one_or_none()
    
    if not role:
        return []
    
    # 超级管理员拥有所有权限
    if role.role_code == "super_admin":
        from app.core.permissions import SUPER_ADMIN_PERMISSIONS
        return SUPER_ADMIN_PERMISSIONS
    
    # 查询角色的资源权限
    result = await db.execute(
        select(SysResource.code)
        .join(SysRoleResource, SysRoleResource.resource_id == SysResource.id)
        .where(SysRoleResource.role_id == role.id)
    )
    permissions = [row[0] for row in result.fetchall()]
    
    return permissions


def require_permission(permission_code: str):
    """
    权限装饰器
    用法: @require_permission("user:edit")
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: SysUser = None, db: AsyncSession = None, **kwargs):
            # 获取用户权限
            permissions = await get_user_permissions(db, current_user)
            
            # 检查权限
            if permission_code not in permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="权限不足"
                )
            
            # 调用原函数
            return await func(*args, current_user=current_user, db=db, **kwargs)
        return wrapper
    return decorator


class PermissionChecker:
    """权限检查器 - 用于依赖注入"""
    
    def __init__(self, permission_code: str):
        self.permission_code = permission_code
    
    async def __call__(
        self,
        current_user: SysUser = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ):
        permissions = await get_user_permissions(db, current_user)
        
        if self.permission_code not in permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )
        
        return current_user
