"""
数据库模型初始化
"""
from app.models.sys_user import SysUser
from app.models.sys_role import SysRole, SysRoleMenu
from app.models.sys_menu import SysMenu
from app.models.sys_resource import SysResource, SysRoleResource
from app.models.warehouse import WarehouseInfo, ProductionLine, WarehouseShelf, WarehouseLocation
from app.models.material import (
    MaterialType, MaterialBoxType, MaterialStock,
    MaterialOutboundRecord, MaterialBoxInfo
)
from app.models.order import (
    OrderInfo, OrderInDetail, OrderOutDetail,
    OrderStockDetail, OrderInoutRecord
)
from app.models.device import DeviceType, DeviceInfo, DeviceIot
from app.models.log import SysOperationLog, SysRunLog

__all__ = [
    # User & Permission
    "SysUser",
    "SysRole",
    "SysRoleMenu",
    "SysMenu",
    "SysResource",
    "SysRoleResource",
    # Warehouse
    "WarehouseInfo",
    "ProductionLine",
    "WarehouseShelf",
    "WarehouseLocation",
    # Material
    "MaterialType",
    "MaterialBoxType",
    "MaterialStock",
    "MaterialOutboundRecord",
    "MaterialBoxInfo",
    # Order
    "OrderInfo",
    "OrderInDetail",
    "OrderOutDetail",
    "OrderStockDetail",
    "OrderInoutRecord",
    # Device
    "DeviceType",
    "DeviceInfo",
    "DeviceIot",
    # Log
    "SysOperationLog",
    "SysRunLog",
]
