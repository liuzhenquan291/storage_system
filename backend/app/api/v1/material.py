"""
物资管理 API
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime

from app.core.database import get_db
from app.schemas.response import success_response, error_response
from app.models.material import (
    MaterialType, MaterialBoxType, MaterialStock,
    MaterialOutboundRecord, MaterialBoxInfo
)
from app.models.sys_user import SysUser
from app.middleware.auth import get_current_user, PermissionChecker

router = APIRouter()


# ============ 物资类型管理 ============

@router.get("/type", summary="获取物资类型列表")
async def get_material_types(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    type_name: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(PermissionChecker("material:view"))
):
    """获取物资类型列表"""
    query = select(MaterialType)
    count_query = select(func.count(MaterialType.id))
    
    if type_name:
        query = query.where(MaterialType.type_name.like(f"%{type_name}%"))
        count_query = count_query.where(MaterialType.type_name.like(f"%{type_name}%"))
    
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    types = result.scalars().all()
    
    count_result = await db.execute(count_query)
    total = count_result.scalar()
    
    return success_response(data={
        "list": [t.to_dict() for t in types],
        "total": total,
        "page": page,
        "page_size": page_size
    })


@router.post("/type", summary="创建物资类型")
async def create_material_type(
    type_code: str = Body(..., description="类型编码"),
    type_name: str = Body(..., description="类型名称"),
    specification: Optional[str] = Body(None, description="规格"),
    unit: Optional[str] = Body(None, description="单位"),
    description: Optional[str] = Body(None, description="描述"),
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(PermissionChecker("material:edit"))
):
    """创建物资类型"""
    material_type = MaterialType(
        type_code=type_code,
        type_name=type_name,
        specification=specification,
        unit=unit,
        description=description
    )
    db.add(material_type)
    await db.commit()
    
    return success_response(data=material_type.to_dict(), message="创建成功")


# ============ 在库物资管理 ============

@router.get("/stock", summary="获取在库物资列表")
async def get_material_stocks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    warehouse_id: Optional[int] = None,
    type_id: Optional[int] = None,
    material_name: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(PermissionChecker("material:view"))
):
    """获取在库物资列表"""
    query = select(MaterialStock)
    count_query = select(func.count(MaterialStock.id))
    
    if warehouse_id:
        query = query.where(MaterialStock.warehouse_id == warehouse_id)
        count_query = count_query.where(MaterialStock.warehouse_id == warehouse_id)
    
    if type_id:
        query = query.where(MaterialStock.type_id == type_id)
        count_query = count_query.where(MaterialStock.type_id == type_id)
    
    if material_name:
        query = query.where(MaterialStock.material_name.like(f"%{material_name}%"))
        count_query = count_query.where(MaterialStock.material_name.like(f"%{material_name}%"))
    
    query = query.offset((page - 1) * page_size).limit(page_size)
    query = query.order_by(MaterialStock.created_time.desc())
    
    result = await db.execute(query)
    stocks = result.scalars().all()
    
    count_result = await db.execute(count_query)
    total = count_result.scalar()
    
    return success_response(data={
        "list": [s.to_dict() for s in stocks],
        "total": total,
        "page": page,
        "page_size": page_size
    })


@router.get("/stock/{stock_id}", summary="获取物资详情")
async def get_material_stock(
    stock_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """获取物资详情"""
    result = await db.execute(
        select(MaterialStock).where(MaterialStock.id == stock_id)
    )
    stock = result.scalar_one_or_none()
    
    if not stock:
        return error_response(message="物资不存在", code=404)
    
    return success_response(data=stock.to_dict())


# ============ 出库记录管理 ============

@router.get("/outbound-record", summary="获取出库记录列表")
async def get_outbound_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    warehouse_id: Optional[int] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(PermissionChecker("record:view"))
):
    """获取出库记录列表"""
    query = select(MaterialOutboundRecord)
    count_query = select(func.count(MaterialOutboundRecord.id))
    
    if warehouse_id:
        query = query.where(MaterialOutboundRecord.warehouse_id == warehouse_id)
        count_query = count_query.where(MaterialOutboundRecord.warehouse_id == warehouse_id)
    
    if start_time:
        query = query.where(MaterialOutboundRecord.outbound_time >= start_time)
        count_query = count_query.where(MaterialOutboundRecord.outbound_time >= start_time)
    
    if end_time:
        query = query.where(MaterialOutboundRecord.outbound_time <= end_time)
        count_query = count_query.where(MaterialOutboundRecord.outbound_time <= end_time)
    
    query = query.offset((page - 1) * page_size).limit(page_size)
    query = query.order_by(MaterialOutboundRecord.outbound_time.desc())
    
    result = await db.execute(query)
    records = result.scalars().all()
    
    count_result = await db.execute(count_query)
    total = count_result.scalar()
    
    return success_response(data={
        "list": [r.to_dict() for r in records],
        "total": total,
        "page": page,
        "page_size": page_size
    })


# ============ 料箱管理 ============

@router.get("/box", summary="获取料箱列表")
async def get_material_boxes(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    warehouse_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """获取料箱列表"""
    query = select(MaterialBoxInfo)
    count_query = select(func.count(MaterialBoxInfo.id))
    
    if warehouse_id:
        query = query.where(MaterialBoxInfo.warehouse_id == warehouse_id)
        count_query = count_query.where(MaterialBoxInfo.warehouse_id == warehouse_id)
    
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    boxes = result.scalars().all()
    
    count_result = await db.execute(count_query)
    total = count_result.scalar()
    
    return success_response(data={
        "list": [b.to_dict() for b in boxes],
        "total": total,
        "page": page,
        "page_size": page_size
    })


@router.post("/box", summary="创建料箱")
async def create_material_box(
    box_code: str = Body(..., description="料箱编码"),
    box_type_id: int = Body(..., description="料箱类型ID"),
    warehouse_id: Optional[int] = Body(None, description="库房ID"),
    location_id: Optional[int] = Body(None, description="库位ID"),
    capacity: int = Body(100, description="容量"),
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """创建料箱"""
    box = MaterialBoxInfo(
        box_code=box_code,
        box_type_id=box_type_id,
        warehouse_id=warehouse_id,
        location_id=location_id,
        capacity=capacity
    )
    db.add(box)
    await db.commit()
    
    return success_response(data=box.to_dict(), message="创建成功")
