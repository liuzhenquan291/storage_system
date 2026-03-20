"""
菜单管理 API
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.schemas.response import success_response, error_response
from app.models.sys_menu import SysMenu
from app.models.sys_user import SysUser
from app.middleware.auth import get_current_user

router = APIRouter()


@router.get("", summary="获取菜单列表")
async def get_menus(
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """获取菜单列表（树形结构）"""
    result = await db.execute(
        select(SysMenu).where(SysMenu.status == 1).order_by(SysMenu.sort_order)
    )
    menus = result.scalars().all()
    
    # 构建树形结构
    menu_list = [m.to_dict() for m in menus]
    
    return success_response(data=menu_list)


@router.post("", summary="创建菜单")
async def create_menu(
    menu_name: str,
    menu_code: Optional[str] = None,
    parent_id: int = 0,
    menu_path: Optional[str] = None,
    menu_icon: Optional[str] = None,
    menu_type: int = 1,
    sort_order: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """创建菜单"""
    menu = SysMenu(
        menu_name=menu_name,
        menu_code=menu_code,
        parent_id=parent_id,
        menu_path=menu_path,
        menu_icon=menu_icon,
        menu_type=menu_type,
        sort_order=sort_order
    )
    db.add(menu)
    await db.commit()
    
    return success_response(data=menu.to_dict(), message="创建成功")


@router.put("/{menu_id}", summary="更新菜单")
async def update_menu(
    menu_id: int,
    menu_name: Optional[str] = None,
    menu_path: Optional[str] = None,
    menu_icon: Optional[str] = None,
    sort_order: Optional[int] = None,
    status: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """更新菜单"""
    result = await db.execute(
        select(SysMenu).where(SysMenu.id == menu_id)
    )
    menu = result.scalar_one_or_none()
    
    if not menu:
        return error_response(message="菜单不存在", code=404)
    
    if menu_name:
        menu.menu_name = menu_name
    if menu_path is not None:
        menu.menu_path = menu_path
    if menu_icon is not None:
        menu.menu_icon = menu_icon
    if sort_order is not None:
        menu.sort_order = sort_order
    if status is not None:
        menu.status = status
    
    await db.commit()
    
    return success_response(data=menu.to_dict(), message="更新成功")


@router.delete("/{menu_id}", summary="删除菜单")
async def delete_menu(
    menu_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """删除菜单"""
    # 检查是否有子菜单
    result = await db.execute(
        select(func.count(SysMenu.id)).where(SysMenu.parent_id == menu_id)
    )
    if result.scalar() > 0:
        return error_response(message="存在子菜单，无法删除", code=400)
    
    result = await db.execute(
        select(SysMenu).where(SysMenu.id == menu_id)
    )
    menu = result.scalar_one_or_none()
    
    if not menu:
        return error_response(message="菜单不存在", code=404)
    
    await db.delete(menu)
    await db.commit()
    
    return success_response(message="删除成功")


@router.get("/user", summary="获取用户菜单")
async def get_user_menus(
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """获取当前用户的菜单"""
    from app.models.sys_role import SysRoleMenu
    
    # 超级管理员获取所有菜单
    if current_user.role_id:
        # 查询角色关联的菜单
        result = await db.execute(
            select(SysMenu)
            .join(SysRoleMenu, SysMenu.id == SysRoleMenu.menu_id)
            .where(SysRoleMenu.role_id == current_user.role_id, SysMenu.status == 1)
            .order_by(SysMenu.sort_order)
        )
        menus = result.scalars().all()
    else:
        menus = []
    
    return success_response(data=[m.to_dict() for m in menus])
