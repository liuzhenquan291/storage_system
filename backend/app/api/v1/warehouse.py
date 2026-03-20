"""
库房管理 API
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.core.code_generator import (
    generate_unique_code, validate_code, CODE_PREFIXES
)
from app.schemas.response import success_response, error_response
from app.models.warehouse import WarehouseInfo, ProductionLine, WarehouseShelf, WarehouseLocation
from app.middleware.auth import PermissionChecker

router = APIRouter()


# ============ 库房管理 ============

@router.get("/info", summary="获取库房列表")
async def get_warehouses(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    warehouse_name: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(PermissionChecker("warehouse:view"))
):
    """获取库房列表"""
    query = select(WarehouseInfo)
    count_query = select(func.count(WarehouseInfo.id))
    
    if warehouse_name:
        query = query.where(WarehouseInfo.warehouse_name.like(f"%{warehouse_name}%"))
        count_query = count_query.where(WarehouseInfo.warehouse_name.like(f"%{warehouse_name}%"))
    
    query = query.offset((page - 1) * page_size).limit(page_size)
    query = query.order_by(WarehouseInfo.created_time.desc())
    
    result = await db.execute(query)
    warehouses = result.scalars().all()
    
    count_result = await db.execute(count_query)
    total = count_result.scalar()
    
    return success_response(data={
        "list": [w.to_dict() for w in warehouses],
        "total": total,
        "page": page,
        "page_size": page_size
    })


@router.get("/info/dropdown", summary="获取库房下拉列表")
async def get_warehouse_dropdown(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(PermissionChecker("warehouse:view"))
):
    """获取库房下拉列表（用于选择）"""
    result = await db.execute(
        select(WarehouseInfo)
        .where(WarehouseInfo.status == 1)
        .order_by(WarehouseInfo.warehouse_code)
    )
    warehouses = result.scalars().all()
    
    return success_response(data=[{
        "id": w.id,
        "code": w.warehouse_code,
        "name": w.warehouse_name,
        "label": f"{w.warehouse_code} - {w.warehouse_name}"
    } for w in warehouses])


@router.post("/info", summary="创建库房")
async def create_warehouse(
    warehouse_name: str = Body(..., description="库房名称", min_length=2, max_length=100),
    description: Optional[str] = Body(None, description="库房描述"),
    address: Optional[str] = Body(None, description="库房地址"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(PermissionChecker("warehouse:edit"))
):
    """创建库房 - 自动生成编号 WH-0001 格式"""
    # 自动生成编号
    warehouse_code = await generate_unique_code(
        db, WarehouseInfo, "warehouse_code", "warehouse"
    )
    
    warehouse = WarehouseInfo(
        warehouse_code=warehouse_code,
        warehouse_name=warehouse_name,
        description=description,
        address=address,
        created_by=current_user.id
    )
    db.add(warehouse)
    await db.commit()
    
    return success_response(data=warehouse.to_dict(), message=f"创建成功，编号：{warehouse_code}")


@router.put("/info/{warehouse_id}", summary="更新库房")
async def update_warehouse(
    warehouse_id: int,
    warehouse_name: Optional[str] = Body(None, description="库房名称"),
    description: Optional[str] = Body(None, description="库房描述"),
    address: Optional[str] = Body(None, description="库房地址"),
    status: Optional[int] = Body(None, description="状态"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(PermissionChecker("warehouse:edit"))
):
    """更新库房"""
    result = await db.execute(
        select(WarehouseInfo).where(WarehouseInfo.id == warehouse_id)
    )
    warehouse = result.scalar_one_or_none()
    
    if not warehouse:
        return error_response(message="库房不存在", code=404)
    
    if warehouse_name:
        warehouse.warehouse_name = warehouse_name
    if description is not None:
        warehouse.description = description
    if address is not None:
        warehouse.address = address
    if status is not None:
        warehouse.status = status
    
    await db.commit()
    
    return success_response(data=warehouse.to_dict(), message="更新成功")


@router.delete("/info/{warehouse_id}", summary="删除库房")
async def delete_warehouse(
    warehouse_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(PermissionChecker("warehouse:edit"))
):
    """删除库房"""
    result = await db.execute(
        select(WarehouseInfo).where(WarehouseInfo.id == warehouse_id)
    )
    warehouse = result.scalar_one_or_none()
    
    if not warehouse:
        return error_response(message="库房不存在", code=404)
    
    await db.delete(warehouse)
    await db.commit()
    
    return success_response(message="删除成功")


# ============ 产线管理 ============

@router.get("/line", summary="获取产线列表")
async def get_lines(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    warehouse_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(PermissionChecker("warehouse:view"))
):
    """获取产线列表"""
    query = select(ProductionLine)
    count_query = select(func.count(ProductionLine.id))
    
    if warehouse_id:
        query = query.where(ProductionLine.warehouse_id == warehouse_id)
        count_query = count_query.where(ProductionLine.warehouse_id == warehouse_id)
    
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    lines = result.scalars().all()
    
    count_result = await db.execute(count_query)
    total = count_result.scalar()
    
    return success_response(data={
        "list": [l.to_dict() for l in lines],
        "total": total,
        "page": page,
        "page_size": page_size
    })


@router.get("/line/dropdown", summary="获取产线下拉列表")
async def get_line_dropdown(
    warehouse_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(PermissionChecker("warehouse:view"))
):
    """获取产线下拉列表（用于选择）"""
    query = select(ProductionLine).where(ProductionLine.status == 1)
    
    if warehouse_id:
        query = query.where(ProductionLine.warehouse_id == warehouse_id)
    
    query = query.order_by(ProductionLine.line_code)
    result = await db.execute(query)
    lines = result.scalars().all()
    
    return success_response(data=[{
        "id": l.id,
        "code": l.line_code,
        "name": l.line_name,
        "warehouse_id": l.warehouse_id,
        "label": f"{l.line_code} - {l.line_name}"
    } for l in lines])


@router.post("/line", summary="创建产线")
async def create_line(
    line_name: str = Body(..., description="产线名称", min_length=2, max_length=100),
    warehouse_id: int = Body(..., description="所属库房ID"),
    description: Optional[str] = Body(None, description="产线描述"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(PermissionChecker("warehouse:edit"))
):
    """创建产线 - 自动生成编号 PL-0001 格式"""
    # 自动生成编号
    line_code = await generate_unique_code(
        db, ProductionLine, "line_code", "production_line"
    )
    
    line = ProductionLine(
        line_code=line_code,
        line_name=line_name,
        warehouse_id=warehouse_id,
        description=description
    )
    db.add(line)
    await db.commit()
    
    return success_response(data=line.to_dict(), message=f"创建成功，编号：{line_code}")


# ============ 货架管理 ============

@router.get("/shelf", summary="获取货架列表")
async def get_shelves(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    warehouse_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(PermissionChecker("warehouse:view"))
):
    """获取货架列表"""
    query = select(WarehouseShelf)
    count_query = select(func.count(WarehouseShelf.id))
    
    if warehouse_id:
        query = query.where(WarehouseShelf.warehouse_id == warehouse_id)
        count_query = count_query.where(WarehouseShelf.warehouse_id == warehouse_id)
    
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    shelves = result.scalars().all()
    
    count_result = await db.execute(count_query)
    total = count_result.scalar()
    
    return success_response(data={
        "list": [s.to_dict() for s in shelves],
        "total": total,
        "page": page,
        "page_size": page_size
    })


@router.get("/shelf/dropdown", summary="获取货架下拉列表")
async def get_shelf_dropdown(
    warehouse_id: Optional[int] = None,
    line_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(PermissionChecker("warehouse:view"))
):
    """获取货架下拉列表（用于选择）"""
    query = select(WarehouseShelf).where(WarehouseShelf.status == 1)
    
    if warehouse_id:
        query = query.where(WarehouseShelf.warehouse_id == warehouse_id)
    if line_id:
        query = query.where(WarehouseShelf.line_id == line_id)
    
    query = query.order_by(WarehouseShelf.shelf_code)
    result = await db.execute(query)
    shelves = result.scalars().all()
    
    return success_response(data=[{
        "id": s.id,
        "code": s.shelf_code,
        "name": s.shelf_name,
        "warehouse_id": s.warehouse_id,
        "line_id": s.line_id,
        "label": f"{s.shelf_code} - {s.shelf_name}"
    } for s in shelves])


@router.post("/shelf", summary="创建货架")
async def create_shelf(
    shelf_name: str = Body(..., description="货架名称", min_length=2, max_length=100),
    warehouse_id: int = Body(..., description="所属库房ID"),
    line_id: Optional[int] = Body(None, description="所属产线ID"),
    shelf_type: int = Body(1, description="货架类型：1-单伸位，2-双伸位"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(PermissionChecker("warehouse:edit"))
):
    """创建货架 - 自动生成编号 SF-0001 格式"""
    # 自动生成编号
    shelf_code = await generate_unique_code(
        db, WarehouseShelf, "shelf_code", "shelf"
    )
    
    shelf = WarehouseShelf(
        shelf_code=shelf_code,
        shelf_name=shelf_name,
        shelf_no=shelf_code.split("-")[1],  # 使用编号后四位作为序号
        warehouse_id=warehouse_id,
        line_id=line_id,
        shelf_type=shelf_type
    )
    db.add(shelf)
    await db.commit()
    
    return success_response(data=shelf.to_dict(), message=f"创建成功，编号：{shelf_code}")


# ============ 库位管理 ============

@router.get("/location", summary="获取库位列表")
async def get_locations(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    shelf_id: Optional[int] = None,
    warehouse_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(PermissionChecker("warehouse:view"))
):
    """获取库位列表"""
    query = select(WarehouseLocation)
    count_query = select(func.count(WarehouseLocation.id))
    
    if shelf_id:
        query = query.where(WarehouseLocation.shelf_id == shelf_id)
        count_query = count_query.where(WarehouseLocation.shelf_id == shelf_id)
    
    if warehouse_id:
        query = query.where(WarehouseLocation.warehouse_id == warehouse_id)
        count_query = count_query.where(WarehouseLocation.warehouse_id == warehouse_id)
    
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    locations = result.scalars().all()
    
    count_result = await db.execute(count_query)
    total = count_result.scalar()
    
    return success_response(data={
        "list": [l.to_dict() for l in locations],
        "total": total,
        "page": page,
        "page_size": page_size
    })


@router.get("/location/dropdown", summary="获取库位下拉列表")
async def get_location_dropdown(
    shelf_id: Optional[int] = None,
    warehouse_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(PermissionChecker("warehouse:view"))
):
    """获取库位下拉列表（用于选择）"""
    query = select(WarehouseLocation).where(WarehouseLocation.status == 1)
    
    if shelf_id:
        query = query.where(WarehouseLocation.shelf_id == shelf_id)
    if warehouse_id:
        query = query.where(WarehouseLocation.warehouse_id == warehouse_id)
    
    query = query.order_by(WarehouseLocation.location_code)
    result = await db.execute(query)
    locations = result.scalars().all()
    
    return success_response(data=[{
        "id": l.id,
        "code": l.location_code,
        "shelf_id": l.shelf_id,
        "warehouse_id": l.warehouse_id,
        "label": l.location_code
    } for l in locations])


@router.post("/location", summary="创建库位")
async def create_location(
    shelf_id: int = Body(..., description="所属货架ID"),
    warehouse_id: int = Body(..., description="所属库房ID"),
    row_no: int = Body(..., description="排号", ge=1),
    col_no: int = Body(..., description="列号", ge=1),
    layer_no: int = Body(..., description="层号", ge=1),
    line_id: Optional[int] = Body(None, description="所属产线ID"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(PermissionChecker("warehouse:edit"))
):
    """创建库位 - 自动生成编号 LC-0001 格式"""
    # 自动生成编号
    location_code = await generate_unique_code(
        db, WarehouseLocation, "location_code", "location"
    )
    
    location = WarehouseLocation(
        location_code=location_code,
        shelf_id=shelf_id,
        warehouse_id=warehouse_id,
        line_id=line_id,
        row_no=row_no,
        col_no=col_no,
        layer_no=layer_no
    )
    db.add(location)
    await db.commit()
    
    return success_response(data=location.to_dict(), message=f"创建成功，编号：{location_code}")


@router.post("/location/batch", summary="批量创建库位")
async def batch_create_locations(
    shelf_id: int = Body(..., description="货架ID"),
    warehouse_id: int = Body(..., description="库房ID"),
    rows: int = Body(..., description="行数", ge=1, le=99),
    cols: int = Body(..., description="列数", ge=1, le=99),
    layers: int = Body(..., description="层数", ge=1, le=99),
    line_id: Optional[int] = Body(None, description="产线ID"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(PermissionChecker("warehouse:edit"))
):
    """批量创建库位 - 自动生成编号 LC-0001 格式"""
    from app.core.code_generator import get_next_sequence, generate_code
    
    # 先获取当前最大序号
    prefix = "LC"
    total_count = rows * cols * layers
    start_seq = await get_next_sequence(db, WarehouseLocation, "location_code", prefix)
    
    locations = []
    seq = start_seq
    
    for row in range(1, rows + 1):
        for col in range(1, cols + 1):
            for layer in range(1, layers + 1):
                location_code = generate_code(prefix, seq)
                seq += 1
                
                location = WarehouseLocation(
                    location_code=location_code,
                    shelf_id=shelf_id,
                    warehouse_id=warehouse_id,
                    line_id=line_id,
                    row_no=row,
                    col_no=col,
                    layer_no=layer
                )
                db.add(location)
                locations.append(location_code)
    
    await db.commit()
    
    return success_response(
        data={"count": len(locations), "locations": locations},
        message=f"成功创建 {len(locations)} 个库位"
    )


@router.get("/code-prefixes", summary="获取编号前缀定义")
async def get_code_prefixes(
    current_user = Depends(PermissionChecker("warehouse:view"))
):
    """获取各类实体的编号前缀定义"""
    return success_response(data=CODE_PREFIXES)
