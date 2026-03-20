"""
工单管理 API
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime
import random

from app.core.database import get_db
from app.schemas.response import success_response, error_response
from app.models.order import (
    OrderInfo, OrderInDetail, OrderOutDetail,
    OrderStockDetail, OrderInoutRecord
)
from app.models.material import MaterialStock, MaterialOutboundRecord
from app.models.warehouse import WarehouseLocation
from app.models.sys_user import SysUser
from app.middleware.auth import get_current_user, PermissionChecker

router = APIRouter()


def generate_order_code(order_type: int) -> str:
    """生成工单号"""
    prefix = {1: "IN", 2: "OUT", 3: "CHK"}
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_num = random.randint(1000, 9999)
    return f"{prefix.get(order_type, 'ORD')}{timestamp}{random_num}"


# ============ 入库任务 ============

@router.get("/inbound", summary="获取入库任务列表")
async def get_inbound_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    warehouse_id: Optional[int] = None,
    status: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(PermissionChecker("order:inbound"))
):
    """获取入库任务列表"""
    query = select(OrderInfo).where(OrderInfo.order_type == 1, OrderInfo.deleted == 0)
    count_query = select(func.count(OrderInfo.id)).where(OrderInfo.order_type == 1, OrderInfo.deleted == 0)
    
    if warehouse_id:
        query = query.where(OrderInfo.warehouse_id == warehouse_id)
        count_query = count_query.where(OrderInfo.warehouse_id == warehouse_id)
    
    if status is not None:
        query = query.where(OrderInfo.status == status)
        count_query = count_query.where(OrderInfo.status == status)
    
    query = query.offset((page - 1) * page_size).limit(page_size)
    query = query.order_by(OrderInfo.created_time.desc())
    
    result = await db.execute(query)
    orders = result.scalars().all()
    
    count_result = await db.execute(count_query)
    total = count_result.scalar()
    
    return success_response(data={
        "list": [o.to_dict() for o in orders],
        "total": total,
        "page": page,
        "page_size": page_size
    })


@router.post("/inbound", summary="创建入库任务")
async def create_inbound_order(
    warehouse_id: int = Body(..., description="库房ID"),
    items: list[dict] = Body(..., description="入库明细列表"),
    line_id: Optional[int] = Body(None, description="产线ID"),
    remark: Optional[str] = Body(None, description="备注"),
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(PermissionChecker("order:inbound"))
):
    """创建入库任务"""
    order_code = generate_order_code(1)
    plan_quantity = sum(item.get("quantity", 0) for item in items)
    
    order = OrderInfo(
        order_code=order_code,
        order_type=1,
        warehouse_id=warehouse_id,
        line_id=line_id,
        plan_quantity=plan_quantity,
        status=0,
        remark=remark,
        created_by=current_user.id
    )
    db.add(order)
    await db.flush()
    
    # 创建入库明细
    for item in items:
        detail = OrderInDetail(
            order_id=order.id,
            material_code=item.get("material_code"),
            material_name=item.get("material_name"),
            type_id=item.get("type_id"),
            quantity=item.get("quantity"),
            unit=item.get("unit"),
            location_id=item.get("location_id"),
            batch_no=item.get("batch_no")
        )
        db.add(detail)
    
    await db.commit()
    
    return success_response(data=order.to_dict(), message="入库任务创建成功")


@router.post("/inbound/{order_id}/execute", summary="执行入库任务")
async def execute_inbound_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(PermissionChecker("order:inbound"))
):
    """执行入库任务"""
    result = await db.execute(
        select(OrderInfo).where(OrderInfo.id == order_id, OrderInfo.order_type == 1)
    )
    order = result.scalar_one_or_none()
    
    if not order:
        return error_response(message="入库任务不存在", code=404)
    
    if order.status != 0:
        return error_response(message="任务状态不允许执行", code=400)
    
    # 获取入库明细
    detail_result = await db.execute(
        select(OrderInDetail).where(OrderInDetail.order_id == order_id)
    )
    details = detail_result.scalars().all()
    
    total_quantity = 0
    
    for detail in details:
        # 创建库存记录
        stock = MaterialStock(
            material_code=detail.material_code,
            material_name=detail.material_name,
            type_id=detail.type_id,
            quantity=detail.quantity,
            unit=detail.unit,
            location_id=detail.location_id,
            warehouse_id=order.warehouse_id,
            batch_no=detail.batch_no,
            status=1,
            inbound_time=datetime.now()
        )
        db.add(stock)
        
        # 更新库位状态
        if detail.location_id:
            await db.execute(
                WarehouseLocation.__table__.update()
                .where(WarehouseLocation.id == detail.location_id)
                .values(status=2)
            )
        
        # 记录入库操作
        record = OrderInoutRecord(
            order_id=order.id,
            order_code=order.order_code,
            order_type=1,
            material_code=detail.material_code,
            material_name=detail.material_name,
            quantity=detail.quantity,
            operation_type=1,
            before_quantity=0,
            after_quantity=detail.quantity,
            operator_id=current_user.id,
            operator_name=current_user.real_name,
            warehouse_id=order.warehouse_id,
            location_id=detail.location_id
        )
        db.add(record)
        
        total_quantity += detail.quantity
    
    # 更新工单状态
    order.status = 2
    order.actual_quantity = total_quantity
    order.operator_id = current_user.id
    order.operator_name = current_user.real_name
    order.start_time = datetime.now()
    order.end_time = datetime.now()
    
    await db.commit()
    
    return success_response(message="入库任务执行成功")


# ============ 出库任务 ============

@router.get("/outbound", summary="获取出库任务列表")
async def get_outbound_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    warehouse_id: Optional[int] = None,
    status: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(PermissionChecker("order:outbound"))
):
    """获取出库任务列表"""
    query = select(OrderInfo).where(OrderInfo.order_type == 2, OrderInfo.deleted == 0)
    count_query = select(func.count(OrderInfo.id)).where(OrderInfo.order_type == 2, OrderInfo.deleted == 0)
    
    if warehouse_id:
        query = query.where(OrderInfo.warehouse_id == warehouse_id)
        count_query = count_query.where(OrderInfo.warehouse_id == warehouse_id)
    
    if status is not None:
        query = query.where(OrderInfo.status == status)
        count_query = count_query.where(OrderInfo.status == status)
    
    query = query.offset((page - 1) * page_size).limit(page_size)
    query = query.order_by(OrderInfo.created_time.desc())
    
    result = await db.execute(query)
    orders = result.scalars().all()
    
    count_result = await db.execute(count_query)
    total = count_result.scalar()
    
    return success_response(data={
        "list": [o.to_dict() for o in orders],
        "total": total,
        "page": page,
        "page_size": page_size
    })


@router.post("/outbound", summary="创建出库任务")
async def create_outbound_order(
    warehouse_id: int = Body(..., description="库房ID"),
    items: list[dict] = Body(..., description="出库明细列表"),
    line_id: Optional[int] = Body(None, description="产线ID"),
    remark: Optional[str] = Body(None, description="备注"),
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(PermissionChecker("order:outbound"))
):
    """创建出库任务"""
    order_code = generate_order_code(2)
    plan_quantity = sum(item.get("quantity", 0) for item in items)
    
    order = OrderInfo(
        order_code=order_code,
        order_type=2,
        warehouse_id=warehouse_id,
        line_id=line_id,
        plan_quantity=plan_quantity,
        status=0,
        remark=remark,
        created_by=current_user.id
    )
    db.add(order)
    await db.flush()
    
    # 创建出库明细
    for item in items:
        detail = OrderOutDetail(
            order_id=order.id,
            material_code=item.get("material_code"),
            material_name=item.get("material_name"),
            type_id=item.get("type_id"),
            quantity=item.get("quantity"),
            unit=item.get("unit"),
            location_id=item.get("location_id"),
            stock_id=item.get("stock_id")
        )
        db.add(detail)
    
    await db.commit()
    
    return success_response(data=order.to_dict(), message="出库任务创建成功")


@router.post("/outbound/{order_id}/execute", summary="执行出库任务")
async def execute_outbound_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(PermissionChecker("order:outbound"))
):
    """执行出库任务"""
    result = await db.execute(
        select(OrderInfo).where(OrderInfo.id == order_id, OrderInfo.order_type == 2)
    )
    order = result.scalar_one_or_none()
    
    if not order:
        return error_response(message="出库任务不存在", code=404)
    
    if order.status != 0:
        return error_response(message="任务状态不允许执行", code=400)
    
    # 获取出库明细
    detail_result = await db.execute(
        select(OrderOutDetail).where(OrderOutDetail.order_id == order_id)
    )
    details = detail_result.scalars().all()
    
    total_quantity = 0
    
    for detail in details:
        # 获取库存
        stock_result = await db.execute(
            select(MaterialStock).where(MaterialStock.id == detail.stock_id)
        )
        stock = stock_result.scalar_one_or_none()
        
        if not stock or stock.quantity < detail.quantity:
            return error_response(message=f"物资 {detail.material_name} 库存不足", code=400)
        
        before_quantity = stock.quantity
        
        # 扣减库存
        stock.quantity -= detail.quantity
        
        # 如果库存为0，删除库存记录
        if stock.quantity == 0:
            await db.delete(stock)
            # 更新库位状态
            if stock.location_id:
                await db.execute(
                    WarehouseLocation.__table__.update()
                    .where(WarehouseLocation.id == stock.location_id)
                    .values(status=1)
                )
        
        # 创建出库档案
        outbound_record = MaterialOutboundRecord(
            material_code=detail.material_code,
            material_name=detail.material_name,
            type_id=detail.type_id,
            quantity=detail.quantity,
            unit=detail.unit,
            location_id=detail.location_id,
            warehouse_id=order.warehouse_id,
            order_id=order.id,
            operator_id=current_user.id,
            operator_name=current_user.real_name,
            outbound_time=datetime.now()
        )
        db.add(outbound_record)
        
        # 记录出库操作
        record = OrderInoutRecord(
            order_id=order.id,
            order_code=order.order_code,
            order_type=2,
            material_code=detail.material_code,
            material_name=detail.material_name,
            quantity=detail.quantity,
            operation_type=2,
            before_quantity=before_quantity,
            after_quantity=before_quantity - detail.quantity,
            operator_id=current_user.id,
            operator_name=current_user.real_name,
            warehouse_id=order.warehouse_id,
            location_id=detail.location_id
        )
        db.add(record)
        
        total_quantity += detail.quantity
    
    # 更新工单状态
    order.status = 2
    order.actual_quantity = total_quantity
    order.operator_id = current_user.id
    order.operator_name = current_user.real_name
    order.start_time = datetime.now()
    order.end_time = datetime.now()
    
    await db.commit()
    
    return success_response(message="出库任务执行成功")


# ============ 盘点任务 ============

@router.get("/stocktake", summary="获取盘点任务列表")
async def get_stocktake_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    warehouse_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(PermissionChecker("order:stocktake"))
):
    """获取盘点任务列表"""
    query = select(OrderInfo).where(OrderInfo.order_type == 3, OrderInfo.deleted == 0)
    count_query = select(func.count(OrderInfo.id)).where(OrderInfo.order_type == 3, OrderInfo.deleted == 0)
    
    if warehouse_id:
        query = query.where(OrderInfo.warehouse_id == warehouse_id)
        count_query = count_query.where(OrderInfo.warehouse_id == warehouse_id)
    
    query = query.offset((page - 1) * page_size).limit(page_size)
    query = query.order_by(OrderInfo.created_time.desc())
    
    result = await db.execute(query)
    orders = result.scalars().all()
    
    count_result = await db.execute(count_query)
    total = count_result.scalar()
    
    return success_response(data={
        "list": [o.to_dict() for o in orders],
        "total": total,
        "page": page,
        "page_size": page_size
    })


@router.post("/stocktake", summary="创建盘点任务")
async def create_stocktake_order(
    warehouse_id: int = Body(..., description="库房ID"),
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(PermissionChecker("order:stocktake"))
):
    """创建盘点任务"""
    order_code = generate_order_code(3)
    
    order = OrderInfo(
        order_code=order_code,
        order_type=3,
        warehouse_id=warehouse_id,
        status=0,
        created_by=current_user.id
    )
    db.add(order)
    await db.flush()
    
    # 获取该库房所有库存
    stock_result = await db.execute(
        select(MaterialStock).where(MaterialStock.warehouse_id == warehouse_id)
    )
    stocks = stock_result.scalars().all()
    
    # 创建盘点明细
    for stock in stocks:
        detail = OrderStockDetail(
            order_id=order.id,
            material_code=stock.material_code,
            material_name=stock.material_name,
            type_id=stock.type_id,
            book_quantity=stock.quantity,
            actual_quantity=0,
            difference=0,
            location_id=stock.location_id
        )
        db.add(detail)
    
    order.plan_quantity = len(stocks)
    await db.commit()
    
    return success_response(data=order.to_dict(), message="盘点任务创建成功")


# ============ 出入库记录 ============

@router.get("/records", summary="获取出入库记录")
async def get_inout_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    warehouse_id: Optional[int] = None,
    operation_type: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(PermissionChecker("record:view"))
):
    """获取出入库记录"""
    query = select(OrderInoutRecord)
    count_query = select(func.count(OrderInoutRecord.id))
    
    if warehouse_id:
        query = query.where(OrderInoutRecord.warehouse_id == warehouse_id)
        count_query = count_query.where(OrderInoutRecord.warehouse_id == warehouse_id)
    
    if operation_type:
        query = query.where(OrderInoutRecord.operation_type == operation_type)
        count_query = count_query.where(OrderInoutRecord.operation_type == operation_type)
    
    query = query.offset((page - 1) * page_size).limit(page_size)
    query = query.order_by(OrderInoutRecord.operation_time.desc())
    
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
