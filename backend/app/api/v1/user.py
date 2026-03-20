"""
用户管理 API
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.core.security import get_password_hash
from app.schemas.response import success_response, error_response
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.models.sys_user import SysUser
from app.middleware.auth import get_current_user, PermissionChecker

router = APIRouter()


@router.get("", summary="获取用户列表")
async def get_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    username: Optional[str] = None,
    status: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(PermissionChecker("user:view"))
):
    """获取用户列表"""
    # 构建查询
    query = select(SysUser).where(SysUser.deleted == 0)
    count_query = select(func.count(SysUser.id)).where(SysUser.deleted == 0)
    
    if username:
        query = query.where(SysUser.username.like(f"%{username}%"))
        count_query = count_query.where(SysUser.username.like(f"%{username}%"))
    
    if status is not None:
        query = query.where(SysUser.status == status)
        count_query = count_query.where(SysUser.status == status)
    
    # 分页
    query = query.offset((page - 1) * page_size).limit(page_size)
    query = query.order_by(SysUser.created_time.desc())
    
    # 执行查询
    result = await db.execute(query)
    users = result.scalars().all()
    
    count_result = await db.execute(count_query)
    total = count_result.scalar()
    
    return success_response(data={
        "list": [UserResponse(**u.to_dict()) for u in users],
        "total": total,
        "page": page,
        "page_size": page_size
    })


@router.post("", summary="创建用户")
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(PermissionChecker("user:edit"))
):
    """创建用户"""
    # 检查用户名是否存在
    result = await db.execute(
        select(SysUser).where(SysUser.username == user_data.username)
    )
    if result.scalar_one_or_none():
        return error_response(message="用户名已存在", code=400)
    
    # 创建用户
    user = SysUser(
        username=user_data.username,
        password=get_password_hash(user_data.password),
        real_name=user_data.real_name,
        role_id=user_data.role_id,
        warehouse_id=user_data.warehouse_id,
        phone=user_data.phone,
        email=user_data.email,
        created_by=current_user.id,
        status=1
    )
    db.add(user)
    await db.commit()
    
    return success_response(data=UserResponse(**user.to_dict()), message="创建成功")


@router.put("/{user_id}", summary="更新用户")
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(PermissionChecker("user:edit"))
):
    """更新用户"""
    result = await db.execute(
        select(SysUser).where(SysUser.id == user_id, SysUser.deleted == 0)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        return error_response(message="用户不存在", code=404)
    
    # 更新字段
    update_data = user_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)
    
    user.updated_by = current_user.id
    await db.commit()
    
    return success_response(data=UserResponse(**user.to_dict()), message="更新成功")


@router.delete("/{user_id}", summary="删除用户")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(PermissionChecker("user:edit"))
):
    """删除用户（软删除）"""
    result = await db.execute(
        select(SysUser).where(SysUser.id == user_id, SysUser.deleted == 0)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        return error_response(message="用户不存在", code=404)
    
    # 不允许删除自己
    if user.id == current_user.id:
        return error_response(message="不能删除自己的账号", code=400)
    
    user.deleted = 1
    user.updated_by = current_user.id
    await db.commit()
    
    return success_response(message="删除成功")


@router.post("/{user_id}/reset-password", summary="重置密码")
async def reset_password(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(PermissionChecker("user:edit"))
):
    """重置用户密码"""
    result = await db.execute(
        select(SysUser).where(SysUser.id == user_id, SysUser.deleted == 0)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        return error_response(message="用户不存在", code=404)
    
    user.password = get_password_hash("123456")
    user.updated_by = current_user.id
    await db.commit()
    
    return success_response(message="密码已重置为：123456")
