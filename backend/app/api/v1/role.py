"""
角色管理 API
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete

from app.core.database import get_db
from app.schemas.response import success_response, error_response
from app.models.sys_role import SysRole, SysRoleMenu
from app.models.sys_user import SysUser
from app.models.sys_resource import SysResource, SysRoleResource
from app.middleware.auth import get_current_user, PermissionChecker

router = APIRouter()


@router.get("", summary="获取角色列表")
async def get_roles(
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """获取角色列表"""
    query = select(SysRole).where(SysRole.deleted == 0)
    count_query = select(func.count(SysRole.id)).where(SysRole.deleted == 0)
    
    query = query.offset((page - 1) * page_size).limit(page_size)
    query = query.order_by(SysRole.created_time.desc())
    
    result = await db.execute(query)
    roles = result.scalars().all()
    
    count_result = await db.execute(count_query)
    total = count_result.scalar()
    
    # 获取每个角色的权限数量
    role_list = []
    for role in roles:
        role_dict = role.to_dict()
        perm_result = await db.execute(
            select(func.count(SysRoleResource.id)).where(SysRoleResource.role_id == role.id)
        )
        role_dict["permission_count"] = perm_result.scalar() or 0
        role_list.append(role_dict)
    
    return success_response(data={
        "list": role_list,
        "total": total,
        "page": page,
        "page_size": page_size
    })


@router.get("/all", summary="获取所有角色")
async def get_all_roles(
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """获取所有角色（下拉选择用）"""
    query = select(SysRole).where(SysRole.deleted == 0).order_by(SysRole.created_time.desc())
    result = await db.execute(query)
    roles = result.scalars().all()
    
    return success_response(data=[r.to_dict() for r in roles])


@router.get("/{role_id}/permissions", summary="获取角色权限")
async def get_role_permissions(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """获取角色的权限列表"""
    result = await db.execute(
        select(SysResource.code)
        .join(SysRoleResource, SysRoleResource.resource_id == SysResource.id)
        .where(SysRoleResource.role_id == role_id)
    )
    permissions = [row[0] for row in result.fetchall()]
    
    return success_response(data=permissions)


@router.post("", summary="创建角色")
async def create_role(
    role_name: str = Body(..., description="角色名称"),
    role_code: str = Body(..., description="角色编码"),
    description: Optional[str] = Body(None, description="角色描述"),
    permissions: Optional[List[str]] = Body(None, description="权限列表"),
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(PermissionChecker("role:edit"))
):
    """创建角色"""
    # 检查编码是否存在
    result = await db.execute(
        select(SysRole).where(SysRole.role_code == role_code)
    )
    if result.scalar_one_or_none():
        return error_response(message="角色编码已存在", code=400)
    
    role = SysRole(
        role_name=role_name,
        role_code=role_code,
        description=description
    )
    db.add(role)
    await db.flush()
    
    # 分配权限
    if permissions:
        for perm_code in permissions:
            result = await db.execute(
                select(SysResource).where(SysResource.code == perm_code)
            )
            resource = result.scalar_one_or_none()
            if resource:
                role_resource = SysRoleResource(
                    role_id=role.id,
                    resource_id=resource.id
                )
                db.add(role_resource)
    
    await db.commit()
    
    return success_response(data=role.to_dict(), message="创建成功")


@router.put("/{role_id}", summary="更新角色")
async def update_role(
    role_id: int,
    role_name: Optional[str] = Body(None, description="角色名称"),
    description: Optional[str] = Body(None, description="角色描述"),
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(PermissionChecker("role:edit"))
):
    """更新角色基本信息"""
    result = await db.execute(
        select(SysRole).where(SysRole.id == role_id, SysRole.deleted == 0)
    )
    role = result.scalar_one_or_none()
    
    if not role:
        return error_response(message="角色不存在", code=404)
    
    # 不允许修改超级管理员角色
    if role.role_code == "super_admin":
        return error_response(message="超级管理员角色不可修改", code=400)
    
    if role_name:
        role.role_name = role_name
    if description is not None:
        role.description = description
    
    await db.commit()
    
    return success_response(data=role.to_dict(), message="更新成功")


@router.put("/{role_id}/permissions", summary="分配角色权限")
async def update_role_permissions(
    role_id: int,
    permissions: List[str] = Body(..., description="权限列表"),
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(PermissionChecker("role:edit"))
):
    """为角色分配权限"""
    result = await db.execute(
        select(SysRole).where(SysRole.id == role_id, SysRole.deleted == 0)
    )
    role = result.scalar_one_or_none()
    
    if not role:
        return error_response(message="角色不存在", code=404)
    
    # 不允许修改超级管理员角色权限
    if role.role_code == "super_admin":
        return error_response(message="超级管理员角色权限不可修改", code=400)
    
    # 删除原有权限
    await db.execute(
        delete(SysRoleResource).where(SysRoleResource.role_id == role_id)
    )
    
    # 添加新权限
    for perm_code in permissions:
        result = await db.execute(
            select(SysResource).where(SysResource.code == perm_code)
        )
        resource = result.scalar_one_or_none()
        if resource:
            role_resource = SysRoleResource(
                role_id=role.id,
                resource_id=resource.id
            )
            db.add(role_resource)
    
    await db.commit()
    
    return success_response(message="权限分配成功")


@router.delete("/{role_id}", summary="删除角色")
async def delete_role(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(PermissionChecker("role:edit"))
):
    """删除角色"""
    result = await db.execute(
        select(SysRole).where(SysRole.id == role_id, SysRole.deleted == 0)
    )
    role = result.scalar_one_or_none()
    
    if not role:
        return error_response(message="角色不存在", code=404)
    
    # 不允许删除超级管理员角色
    if role.role_code == "super_admin":
        return error_response(message="超级管理员角色不可删除", code=400)
    
    # 检查是否有用户使用
    user_result = await db.execute(
        select(func.count(SysUser.id)).where(SysUser.role_id == role_id, SysUser.deleted == 0)
    )
    if user_result.scalar() > 0:
        return error_response(message="该角色正在被用户使用，无法删除", code=400)
    
    # 删除角色权限关联
    await db.execute(
        delete(SysRoleResource).where(SysRoleResource.role_id == role_id)
    )
    
    role.deleted = 1
    await db.commit()
    
    return success_response(message="删除成功")
