"""
系统资源模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text
from app.core.database import Base


class SysResource(Base):
    """系统资源表"""
    __tablename__ = "sys_resource"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False, comment="资源编码")
    name = Column(String(50), nullable=False, comment="资源名称")
    description = Column(String(200), comment="资源描述")
    created_time = Column(DateTime, default=datetime.now, comment="创建时间")
    
    def to_dict(self):
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "description": self.description,
            "created_time": self.created_time.strftime("%Y-%m-%d %H:%M:%S") if self.created_time else None
        }


class SysRoleResource(Base):
    """角色-资源关联表"""
    __tablename__ = "sys_role_resource"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    role_id = Column(Integer, nullable=False, comment="角色ID")
    resource_id = Column(Integer, nullable=False, comment="资源ID")
    created_time = Column(DateTime, default=datetime.now, comment="创建时间")
