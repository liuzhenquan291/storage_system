"""
系统权限资源配置
"""

# 权限资源列表
PERMISSIONS = [
    {"code": "dashboard:view", "name": "仪表盘查看", "description": "查看系统仪表盘"},
    {"code": "user:view", "name": "用户查看", "description": "查看用户列表"},
    {"code": "user:edit", "name": "用户编辑", "description": "新增、编辑、删除用户"},
    {"code": "role:view", "name": "角色查看", "description": "查看角色列表"},
    {"code": "role:edit", "name": "角色编辑", "description": "新增、编辑、删除角色"},
    {"code": "warehouse:view", "name": "库房查看", "description": "查看库房、产线、货架、库位"},
    {"code": "warehouse:edit", "name": "库房编辑", "description": "新增、编辑、删除库房相关"},
    {"code": "material:view", "name": "物资查看", "description": "查看物资类型、在库物资、出库记录"},
    {"code": "material:edit", "name": "物资编辑", "description": "新增、编辑、删除物资相关"},
    {"code": "order:inbound", "name": "入库权限", "description": "创建和管理入库任务"},
    {"code": "order:outbound", "name": "出库权限", "description": "创建和管理出库任务"},
    {"code": "order:stocktake", "name": "盘点权限", "description": "创建和管理盘点任务"},
    {"code": "record:view", "name": "出入库记录查看", "description": "查看出入库记录"},
    {"code": "device:view", "name": "设备查看", "description": "查看设备信息"},
    {"code": "device:edit", "name": "设备编辑", "description": "新增、编辑、删除设备"},
]

# 超级管理员拥有所有权限
SUPER_ADMIN_PERMISSIONS = [p["code"] for p in PERMISSIONS]
