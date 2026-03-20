"""
角色模型
"""
from sqlalchemy import Column, Integer, String, SmallInteger, DateTime, Text
from datetime import datetime

from app.core.database import Base


class SysRole(Base):
    """系统角色表"""
    __tablename__ = "sys_role"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键")
    role_name = Column(String(50), nullable=False, comment="角色名称")
    role_code = Column(String(50), unique=True, nullable=False, comment="角色编码")
    description = Column(String(255), nullable=True, comment="描述")
    deleted = Column(SmallInteger, default=0, comment="删除标记：0-未删除，1-已删除")
    created_time = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "role_name": self.role_name,
            "role_code": self.role_code,
            "description": self.description,
            "created_time": self.created_time.strftime("%Y-%m-%d %H:%M:%S") if self.created_time else None
        }


class SysRoleMenu(Base):
    """角色菜单关联表"""
    __tablename__ = "sys_role_menu"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键")
    role_id = Column(Integer, nullable=False, comment="角色ID")
    menu_id = Column(Integer, nullable=False, comment="菜单ID")
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "role_id": self.role_id,
            "menu_id": self.menu_id
        }
