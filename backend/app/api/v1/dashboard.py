"""
仪表盘 API
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta

from app.core.database import get_db
from app.schemas.response import success_response
from app.models.warehouse import WarehouseInfo, WarehouseLocation
from app.models.material import MaterialStock
from app.models.order import OrderInfo, OrderInoutRecord
from app.models.sys_user import SysUser
from app.middleware.auth import get_current_user, PermissionChecker

router = APIRouter()


@router.get("/overview", summary="获取仪表盘概览数据")
async def get_overview(
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(PermissionChecker("dashboard:view"))
):
    """获取仪表盘概览数据"""
    
    # 库房统计
    warehouse_result = await db.execute(select(func.count(WarehouseInfo.id)))
    total_warehouses = warehouse_result.scalar() or 0
    
    # 库位统计
    location_result = await db.execute(
        select(func.count(WarehouseLocation.id))
    )
    total_locations = location_result.scalar() or 0
    
    used_location_result = await db.execute(
        select(func.count(WarehouseLocation.id)).where(WarehouseLocation.status == 2)
    )
    used_locations = used_location_result.scalar() or 0
    
    # 物资统计
    stock_result = await db.execute(
        select(func.count(MaterialStock.id))
    )
    total_materials = stock_result.scalar() or 0
    
    quantity_result = await db.execute(
        select(func.sum(MaterialStock.quantity))
    )
    total_quantity = quantity_result.scalar() or 0
    
    # 今日入库
    today = datetime.now().date()
    today_in_result = await db.execute(
        select(func.sum(OrderInoutRecord.quantity))
        .where(
            OrderInoutRecord.operation_type == 1,
            func.date(OrderInoutRecord.operation_time) == today
        )
    )
    today_inbound = today_in_result.scalar() or 0
    
    # 今日出库
    today_out_result = await db.execute(
        select(func.sum(OrderInoutRecord.quantity))
        .where(
            OrderInoutRecord.operation_type == 2,
            func.date(OrderInoutRecord.operation_time) == today
        )
    )
    today_outbound = today_out_result.scalar() or 0
    
    # 待处理工单
    pending_orders_result = await db.execute(
        select(func.count(OrderInfo.id)).where(OrderInfo.status == 0)
    )
    pending_orders = pending_orders_result.scalar() or 0
    
    return success_response(data={
        "warehouse": {
            "total": total_warehouses,
            "locations": {
                "total": total_locations,
                "used": used_locations,
                "usage_rate": round(used_locations / total_locations * 100, 2) if total_locations > 0 else 0
            }
        },
        "material": {
            "total_types": total_materials,
            "total_quantity": total_quantity
        },
        "today": {
            "inbound": today_inbound,
            "outbound": today_outbound
        },
        "order": {
            "pending": pending_orders
        }
    })


@router.get("/chart/inbound-outbound", summary="获取出入库趋势图数据")
async def get_inbound_outbound_chart(
    days: int = 7,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """获取出入库趋势图数据"""
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days - 1)
    
    result = []
    
    for i in range(days):
        current_date = start_date + timedelta(days=i)
        
        # 入库
        in_result = await db.execute(
            select(func.sum(OrderInoutRecord.quantity))
            .where(
                OrderInoutRecord.operation_type == 1,
                func.date(OrderInoutRecord.operation_time) == current_date
            )
        )
        inbound = in_result.scalar() or 0
        
        # 出库
        out_result = await db.execute(
            select(func.sum(OrderInoutRecord.quantity))
            .where(
                OrderInoutRecord.operation_type == 2,
                func.date(OrderInoutRecord.operation_time) == current_date
            )
        )
        outbound = out_result.scalar() or 0
        
        result.append({
            "date": current_date.strftime("%Y-%m-%d"),
            "inbound": inbound,
            "outbound": outbound
        })
    
    return success_response(data=result)


@router.get("/recent-records", summary="获取最近出入库记录")
async def get_recent_records(
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """获取最近出入库记录"""
    result = await db.execute(
        select(OrderInoutRecord)
        .order_by(OrderInoutRecord.operation_time.desc())
        .limit(limit)
    )
    records = result.scalars().all()
    
    return success_response(data=[r.to_dict() for r in records])
