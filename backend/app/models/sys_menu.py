"""
菜单模型
"""
from sqlalchemy import Column, Integer, String, SmallInteger, DateTime
from datetime import datetime

from app.core.database import Base


class SysMenu(Base):
    """系统菜单表"""
    __tablename__ = "sys_menu"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键")
    menu_name = Column(String(50), nullable=False, comment="菜单名称")
    menu_code = Column(String(50), nullable=True, comment="菜单编码")
    parent_id = Column(Integer, default=0, comment="父菜单ID")
    menu_path = Column(String(255), nullable=True, comment="路由路径")
    menu_icon = Column(String(50), nullable=True, comment="图标")
    menu_type = Column(SmallInteger, default=1, comment="类型：0-目录，1-菜单，2-按钮")
    sort_order = Column(Integer, default=0, comment="排序")
    status = Column(SmallInteger, default=1, comment="状态：0-禁用，1-启用")
    created_time = Column(DateTime, default=datetime.now, comment="创建时间")
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "menu_name": self.menu_name,
            "menu_code": self.menu_code,
            "parent_id": self.parent_id,
            "menu_path": self.menu_path,
            "menu_icon": self.menu_icon,
            "menu_type": self.menu_type,
            "sort_order": self.sort_order,
            "status": self.status,
            "created_time": self.created_time.strftime("%Y-%m-%d %H:%M:%S") if self.created_time else None
        }
