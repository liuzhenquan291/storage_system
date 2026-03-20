"""
库房相关模型
"""
from sqlalchemy import Column, Integer, String, SmallInteger, DateTime, Text
from datetime import datetime

from app.core.database import Base


class WarehouseInfo(Base):
    """库房信息表"""
    __tablename__ = "warehouse_info"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键")
    warehouse_code = Column(String(50), unique=True, nullable=False, comment="库房编号")
    warehouse_name = Column(String(100), nullable=False, comment="库房名称")
    description = Column(String(255), nullable=True, comment="描述")
    address = Column(String(255), nullable=True, comment="地址")
    status = Column(SmallInteger, default=1, comment="状态：0-停用，1-启用")
    created_by = Column(Integer, nullable=True, comment="创建人")
    created_time = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    def to_dict(self):
        return {
            "id": self.id,
            "warehouse_code": self.warehouse_code,
            "warehouse_name": self.warehouse_name,
            "description": self.description,
            "address": self.address,
            "status": self.status,
            "created_time": self.created_time.strftime("%Y-%m-%d %H:%M:%S") if self.created_time else None
        }


class ProductionLine(Base):
    """产线信息表"""
    __tablename__ = "production_line"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键")
    line_code = Column(String(50), unique=True, nullable=False, comment="产线编号")
    line_name = Column(String(100), nullable=False, comment="产线名称")
    warehouse_id = Column(Integer, nullable=False, comment="所属库房ID")
    description = Column(String(255), nullable=True, comment="描述")
    status = Column(SmallInteger, default=1, comment="状态：0-停用，1-启用")
    created_time = Column(DateTime, default=datetime.now, comment="创建时间")
    
    def to_dict(self):
        return {
            "id": self.id,
            "line_code": self.line_code,
            "line_name": self.line_name,
            "warehouse_id": self.warehouse_id,
            "description": self.description,
            "status": self.status,
            "created_time": self.created_time.strftime("%Y-%m-%d %H:%M:%S") if self.created_time else None
        }


class WarehouseShelf(Base):
    """货架信息表"""
    __tablename__ = "warehouse_shelf"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键")
    shelf_code = Column(String(50), unique=True, nullable=False, comment="货架编号")
    shelf_no = Column(String(50), nullable=True, comment="货架序号")
    shelf_name = Column(String(100), nullable=False, comment="货架名称")
    warehouse_id = Column(Integer, nullable=False, comment="所属库房ID")
    line_id = Column(Integer, nullable=True, comment="所属产线ID")
    shelf_type = Column(SmallInteger, default=1, comment="货架类型：1-单伸位，2-双伸位")
    status = Column(SmallInteger, default=1, comment="状态：0-停用，1-启用")
    created_time = Column(DateTime, default=datetime.now, comment="创建时间")
    
    def to_dict(self):
        return {
            "id": self.id,
            "shelf_code": self.shelf_code,
            "shelf_no": self.shelf_no,
            "shelf_name": self.shelf_name,
            "warehouse_id": self.warehouse_id,
            "line_id": self.line_id,
            "shelf_type": self.shelf_type,
            "status": self.status,
            "created_time": self.created_time.strftime("%Y-%m-%d %H:%M:%S") if self.created_time else None
        }


class WarehouseLocation(Base):
    """库位信息表"""
    __tablename__ = "warehouse_location"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键")
    location_code = Column(String(50), unique=True, nullable=False, comment="库位编号")
    shelf_id = Column(Integer, nullable=False, comment="所属货架ID")
    warehouse_id = Column(Integer, nullable=False, comment="所属库房ID")
    line_id = Column(Integer, nullable=True, comment="所属产线ID")
    row_no = Column(Integer, nullable=True, comment="排号")
    col_no = Column(Integer, nullable=True, comment="列号")
    layer_no = Column(Integer, nullable=True, comment="层号")
    status = Column(SmallInteger, default=1, comment="状态：0-停用，1-启用，2-占用")
    created_time = Column(DateTime, default=datetime.now, comment="创建时间")
    
    def to_dict(self):
        return {
            "id": self.id,
            "location_code": self.location_code,
            "shelf_id": self.shelf_id,
            "warehouse_id": self.warehouse_id,
            "line_id": self.line_id,
            "row_no": self.row_no,
            "col_no": self.col_no,
            "layer_no": self.layer_no,
            "status": self.status,
            "created_time": self.created_time.strftime("%Y-%m-%d %H:%M:%S") if self.created_time else None
        }
