"""
日志相关模型
"""
from sqlalchemy import Column, Integer, String, SmallInteger, DateTime, Text
from datetime import datetime

from app.core.database import Base


class SysOperationLog(Base):
    """操作日志表"""
    __tablename__ = "sys_operation_log"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键")
    user_id = Column(Integer, nullable=True, comment="操作用户ID")
    username = Column(String(50), nullable=True, comment="操作用户名")
    operation_type = Column(String(50), nullable=True, comment="操作类型")
    operation_desc = Column(String(500), nullable=True, comment="操作描述")
    request_method = Column(String(10), nullable=True, comment="请求方法")
    request_url = Column(String(255), nullable=True, comment="请求URL")
    request_params = Column(Text, nullable=True, comment="请求参数")
    response_result = Column(Text, nullable=True, comment="响应结果")
    ip_address = Column(String(50), nullable=True, comment="IP地址")
    operation_time = Column(DateTime, default=datetime.now, comment="操作时间")
    created_time = Column(DateTime, default=datetime.now, comment="创建时间")
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "username": self.username,
            "operation_type": self.operation_type,
            "operation_desc": self.operation_desc,
            "request_method": self.request_method,
            "request_url": self.request_url,
            "ip_address": self.ip_address,
            "operation_time": self.operation_time.strftime("%Y-%m-%d %H:%M:%S") if self.operation_time else None,
            "created_time": self.created_time.strftime("%Y-%m-%d %H:%M:%S") if self.created_time else None
        }


class SysRunLog(Base):
    """系统运行日志表"""
    __tablename__ = "sys_run_log"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键")
    log_level = Column(String(20), nullable=False, comment="日志级别")
    log_content = Column(Text, nullable=True, comment="日志内容")
    log_source = Column(String(100), nullable=True, comment="日志来源")
    created_time = Column(DateTime, default=datetime.now, comment="创建时间")
    
    def to_dict(self):
        return {
            "id": self.id,
            "log_level": self.log_level,
            "log_content": self.log_content,
            "log_source": self.log_source,
            "created_time": self.created_time.strftime("%Y-%m-%d %H:%M:%S") if self.created_time else None
        }
