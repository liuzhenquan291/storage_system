"""
用户模型
"""
from sqlalchemy import Column, Integer, String, SmallInteger, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class SysUser(Base):
    """系统用户表"""
    __tablename__ = "sys_user"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键")
    username = Column(String(50), unique=True, nullable=False, comment="用户名")
    password = Column(String(255), nullable=False, comment="密码")
    real_name = Column(String(50), nullable=False, comment="真实姓名")
    role_id = Column(Integer, nullable=True, comment="角色ID")
    warehouse_id = Column(Integer, nullable=True, comment="所属库房ID")
    phone = Column(String(20), nullable=True, comment="联系电话")
    email = Column(String(100), nullable=True, comment="邮箱")
    status = Column(SmallInteger, default=1, comment="状态：0-禁用，1-启用")
    deleted = Column(SmallInteger, default=0, comment="删除标记：0-未删除，1-已删除")
    created_by = Column(Integer, nullable=True, comment="创建人")
    created_time = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_by = Column(Integer, nullable=True, comment="更新人")
    updated_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "username": self.username,
            "real_name": self.real_name,
            "role_id": self.role_id,
            "warehouse_id": self.warehouse_id,
            "phone": self.phone,
            "email": self.email,
            "status": self.status,
            "created_time": self.created_time.strftime("%Y-%m-%d %H:%M:%S") if self.created_time else None,
            "updated_time": self.updated_time.strftime("%Y-%m-%d %H:%M:%S") if self.updated_time else None
        }
