"""
设备相关模型
"""
from sqlalchemy import Column, Integer, String, SmallInteger, DateTime
from datetime import datetime

from app.core.database import Base


class DeviceType(Base):
    """设备类型表"""
    __tablename__ = "device_type"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键")
    type_code = Column(String(50), unique=True, nullable=False, comment="类型编码")
    type_name = Column(String(100), nullable=False, comment="类型名称")
    description = Column(String(255), nullable=True, comment="描述")
    created_time = Column(DateTime, default=datetime.now, comment="创建时间")
    
    def to_dict(self):
        return {
            "id": self.id,
            "type_code": self.type_code,
            "type_name": self.type_name,
            "description": self.description,
            "created_time": self.created_time.strftime("%Y-%m-%d %H:%M:%S") if self.created_time else None
        }


class DeviceInfo(Base):
    """设备信息表"""
    __tablename__ = "device_info"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键")
    device_code = Column(String(50), unique=True, nullable=False, comment="设备编号")
    device_name = Column(String(100), nullable=False, comment="设备名称")
    type_id = Column(Integer, nullable=False, comment="设备类型ID")
    line_id = Column(Integer, nullable=True, comment="所属产线ID")
    warehouse_id = Column(Integer, nullable=True, comment="所属库房ID")
    ip_address = Column(String(50), nullable=True, comment="IP地址")
    port = Column(Integer, nullable=True, comment="端口")
    status = Column(SmallInteger, default=0, comment="状态：0-离线，1-在线")
    description = Column(String(255), nullable=True, comment="描述")
    created_time = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    def to_dict(self):
        return {
            "id": self.id,
            "device_code": self.device_code,
            "device_name": self.device_name,
            "type_id": self.type_id,
            "line_id": self.line_id,
            "warehouse_id": self.warehouse_id,
            "ip_address": self.ip_address,
            "port": self.port,
            "status": self.status,
            "description": self.description,
            "created_time": self.created_time.strftime("%Y-%m-%d %H:%M:%S") if self.created_time else None
        }


class DeviceIot(Base):
    """IOT设备表"""
    __tablename__ = "device_iot"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键")
    device_code = Column(String(50), unique=True, nullable=False, comment="设备编号")
    device_name = Column(String(100), nullable=False, comment="设备名称")
    device_type = Column(SmallInteger, nullable=False, comment="设备类型：1-摄像头，2-温湿度传感器，3-大屏")
    ip_address = Column(String(50), nullable=True, comment="IP地址")
    port = Column(Integer, nullable=True, comment="端口")
    warehouse_id = Column(Integer, nullable=True, comment="所属库房ID")
    status = Column(SmallInteger, default=0, comment="状态：0-离线，1-在线")
    description = Column(String(255), nullable=True, comment="描述")
    created_time = Column(DateTime, default=datetime.now, comment="创建时间")
    
    def to_dict(self):
        return {
            "id": self.id,
            "device_code": self.device_code,
            "device_name": self.device_name,
            "device_type": self.device_type,
            "ip_address": self.ip_address,
            "port": self.port,
            "warehouse_id": self.warehouse_id,
            "status": self.status,
            "description": self.description,
            "created_time": self.created_time.strftime("%Y-%m-%d %H:%M:%S") if self.created_time else None
        }
