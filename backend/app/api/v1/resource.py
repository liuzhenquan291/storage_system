"""
资源管理 API
"""
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.schemas.response import success_response
from app.models.sys_resource import SysResource
from app.models.sys_user import SysUser
from app.middleware.auth import get_current_user

router = APIRouter()


@router.get("", summary="获取所有资源")
async def get_resources(
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """获取所有资源列表"""
    result = await db.execute(
        select(SysResource).order_by(SysResource.id)
    )
    resources = result.scalars().all()
    
    return success_response(data=[r.to_dict() for r in resources])


@router.get("/my", summary="获取当前用户权限")
async def get_my_permissions(
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """获取当前用户的权限列表"""
    from app.middleware.auth import get_user_permissions
    
    permissions = await get_user_permissions(db, current_user)
    
    return success_response(data=permissions)
