"""
设备管理 API
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.schemas.response import success_response, error_response
from app.models.device import DeviceType, DeviceInfo, DeviceIot
from app.models.sys_user import SysUser
from app.middleware.auth import get_current_user, PermissionChecker

router = APIRouter()


# ============ 设备类型管理 ============

@router.get("/type", summary="获取设备类型列表")
async def get_device_types(
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """获取设备类型列表"""
    result = await db.execute(select(DeviceType))
    types = result.scalars().all()
    
    return success_response(data=[t.to_dict() for t in types])


@router.post("/type", summary="创建设备类型")
async def create_device_type(
    type_code: str = Body(..., description="类型编码"),
    type_name: str = Body(..., description="类型名称"),
    description: Optional[str] = Body(None, description="描述"),
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """创建设备类型"""
    device_type = DeviceType(
        type_code=type_code,
        type_name=type_name,
        description=description
    )
    db.add(device_type)
    await db.commit()
    
    return success_response(data=device_type.to_dict(), message="创建成功")


# ============ 设备信息管理 ============

@router.get("/info", summary="获取设备列表")
async def get_devices(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    warehouse_id: Optional[int] = None,
    type_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(PermissionChecker("device:view"))
):
    """获取设备列表"""
    query = select(DeviceInfo)
    count_query = select(func.count(DeviceInfo.id))
    
    if warehouse_id:
        query = query.where(DeviceInfo.warehouse_id == warehouse_id)
        count_query = count_query.where(DeviceInfo.warehouse_id == warehouse_id)
    
    if type_id:
        query = query.where(DeviceInfo.type_id == type_id)
        count_query = count_query.where(DeviceInfo.type_id == type_id)
    
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    devices = result.scalars().all()
    
    count_result = await db.execute(count_query)
    total = count_result.scalar()
    
    return success_response(data={
        "list": [d.to_dict() for d in devices],
        "total": total,
        "page": page,
        "page_size": page_size
    })


@router.post("/info", summary="创建设备")
async def create_device(
    device_code: str = Body(..., description="设备编码"),
    device_name: str = Body(..., description="设备名称"),
    type_id: int = Body(..., description="类型ID"),
    warehouse_id: Optional[int] = Body(None, description="库房ID"),
    line_id: Optional[int] = Body(None, description="产线ID"),
    ip_address: Optional[str] = Body(None, description="IP地址"),
    port: Optional[int] = Body(None, description="端口"),
    description: Optional[str] = Body(None, description="描述"),
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(PermissionChecker("device:edit"))
):
    """创建设备"""
    device = DeviceInfo(
        device_code=device_code,
        device_name=device_name,
        type_id=type_id,
        warehouse_id=warehouse_id,
        line_id=line_id,
        ip_address=ip_address,
        port=port,
        description=description
    )
    db.add(device)
    await db.commit()
    
    return success_response(data=device.to_dict(), message="创建成功")


@router.put("/info/{device_id}", summary="更新设备")
async def update_device(
    device_id: int,
    device_name: Optional[str] = Body(None, description="设备名称"),
    ip_address: Optional[str] = Body(None, description="IP地址"),
    port: Optional[int] = Body(None, description="端口"),
    status: Optional[int] = Body(None, description="状态"),
    description: Optional[str] = Body(None, description="描述"),
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(PermissionChecker("device:edit"))
):
    """更新设备"""
    result = await db.execute(
        select(DeviceInfo).where(DeviceInfo.id == device_id)
    )
    device = result.scalar_one_or_none()
    
    if not device:
        return error_response(message="设备不存在", code=404)
    
    if device_name:
        device.device_name = device_name
    if ip_address is not None:
        device.ip_address = ip_address
    if port is not None:
        device.port = port
    if status is not None:
        device.status = status
    if description is not None:
        device.description = description
    
    await db.commit()
    
    return success_response(data=device.to_dict(), message="更新成功")


@router.delete("/info/{device_id}", summary="删除设备")
async def delete_device(
    device_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(PermissionChecker("device:edit"))
):
    """删除设备"""
    result = await db.execute(
        select(DeviceInfo).where(DeviceInfo.id == device_id)
    )
    device = result.scalar_one_or_none()
    
    if not device:
        return error_response(message="设备不存在", code=404)
    
    await db.delete(device)
    await db.commit()
    
    return success_response(message="删除成功")


# ============ IOT设备管理 ============

@router.get("/iot", summary="获取IOT设备列表")
async def get_iot_devices(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    warehouse_id: Optional[int] = None,
    device_type: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(PermissionChecker("device:view"))
):
    """获取IOT设备列表"""
    query = select(DeviceIot)
    count_query = select(func.count(DeviceIot.id))
    
    if warehouse_id:
        query = query.where(DeviceIot.warehouse_id == warehouse_id)
        count_query = count_query.where(DeviceIot.warehouse_id == warehouse_id)
    
    if device_type:
        query = query.where(DeviceIot.device_type == device_type)
        count_query = count_query.where(DeviceIot.device_type == device_type)
    
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    devices = result.scalars().all()
    
    count_result = await db.execute(count_query)
    total = count_result.scalar()
    
    return success_response(data={
        "list": [d.to_dict() for d in devices],
        "total": total,
        "page": page,
        "page_size": page_size
    })


@router.post("/iot", summary="创建IOT设备")
async def create_iot_device(
    device_code: str = Body(..., description="设备编码"),
    device_name: str = Body(..., description="设备名称"),
    device_type: int = Body(..., description="设备类型"),
    warehouse_id: Optional[int] = Body(None, description="库房ID"),
    ip_address: Optional[str] = Body(None, description="IP地址"),
    port: Optional[int] = Body(None, description="端口"),
    description: Optional[str] = Body(None, description="描述"),
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """创建IOT设备"""
    device = DeviceIot(
        device_code=device_code,
        device_name=device_name,
        device_type=device_type,
        warehouse_id=warehouse_id,
        ip_address=ip_address,
        port=port,
        description=description
    )
    db.add(device)
    await db.commit()
    
    return success_response(data=device.to_dict(), message="创建成功")
