"""
物资相关模型
"""
from sqlalchemy import Column, Integer, String, SmallInteger, DateTime, Float
from datetime import datetime

from app.core.database import Base


class MaterialType(Base):
    """物资类型表"""
    __tablename__ = "material_type"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键")
    type_code = Column(String(50), unique=True, nullable=False, comment="类型编码")
    type_name = Column(String(100), nullable=False, comment="类型名称")
    specification = Column(String(255), nullable=True, comment="规格")
    unit = Column(String(20), nullable=True, comment="单位")
    description = Column(String(255), nullable=True, comment="描述")
    status = Column(SmallInteger, default=1, comment="状态：0-停用，1-启用")
    created_time = Column(DateTime, default=datetime.now, comment="创建时间")
    
    def to_dict(self):
        return {
            "id": self.id,
            "type_code": self.type_code,
            "type_name": self.type_name,
            "specification": self.specification,
            "unit": self.unit,
            "description": self.description,
            "status": self.status,
            "created_time": self.created_time.strftime("%Y-%m-%d %H:%M:%S") if self.created_time else None
        }


class MaterialBoxType(Base):
    """料箱类型表"""
    __tablename__ = "material_box_type"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键")
    type_code = Column(String(50), unique=True, nullable=False, comment="类型编码")
    type_name = Column(String(100), nullable=False, comment="类型名称")
    capacity = Column(Integer, default=0, comment="容量")
    description = Column(String(255), nullable=True, comment="描述")
    created_time = Column(DateTime, default=datetime.now, comment="创建时间")
    
    def to_dict(self):
        return {
            "id": self.id,
            "type_code": self.type_code,
            "type_name": self.type_name,
            "capacity": self.capacity,
            "description": self.description,
            "created_time": self.created_time.strftime("%Y-%m-%d %H:%M:%S") if self.created_time else None
        }


class MaterialStock(Base):
    """在库物资表"""
    __tablename__ = "material_stock"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键")
    material_code = Column(String(50), unique=True, nullable=False, comment="物资编号")
    material_name = Column(String(100), nullable=False, comment="物资名称")
    type_id = Column(Integer, nullable=False, comment="物资类型ID")
    quantity = Column(Integer, default=0, comment="数量")
    unit = Column(String(20), nullable=True, comment="单位")
    location_id = Column(Integer, nullable=True, comment="库位ID")
    warehouse_id = Column(Integer, nullable=True, comment="库房ID")
    batch_no = Column(String(50), nullable=True, comment="批次号")
    status = Column(SmallInteger, default=1, comment="状态：1-在库")
    inbound_time = Column(DateTime, nullable=True, comment="入库时间")
    created_time = Column(DateTime, default=datetime.now, comment="创建时间")
    
    def to_dict(self):
        return {
            "id": self.id,
            "material_code": self.material_code,
            "material_name": self.material_name,
            "type_id": self.type_id,
            "quantity": self.quantity,
            "unit": self.unit,
            "location_id": self.location_id,
            "warehouse_id": self.warehouse_id,
            "batch_no": self.batch_no,
            "status": self.status,
            "inbound_time": self.inbound_time.strftime("%Y-%m-%d %H:%M:%S") if self.inbound_time else None,
            "created_time": self.created_time.strftime("%Y-%m-%d %H:%M:%S") if self.created_time else None
        }


class MaterialOutboundRecord(Base):
    """出库物资档案表"""
    __tablename__ = "material_outbound_record"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键")
    material_code = Column(String(50), nullable=False, comment="物资编号")
    material_name = Column(String(100), nullable=False, comment="物资名称")
    type_id = Column(Integer, nullable=False, comment="物资类型ID")
    quantity = Column(Integer, default=0, comment="出库数量")
    unit = Column(String(20), nullable=True, comment="单位")
    location_id = Column(Integer, nullable=True, comment="原库位ID")
    warehouse_id = Column(Integer, nullable=True, comment="库房ID")
    order_id = Column(Integer, nullable=True, comment="出库工单ID")
    outbound_time = Column(DateTime, default=datetime.now, comment="出库时间")
    operator_id = Column(Integer, nullable=True, comment="操作人ID")
    operator_name = Column(String(50), nullable=True, comment="操作人姓名")
    created_time = Column(DateTime, default=datetime.now, comment="创建时间")
    
    def to_dict(self):
        return {
            "id": self.id,
            "material_code": self.material_code,
            "material_name": self.material_name,
            "type_id": self.type_id,
            "quantity": self.quantity,
            "unit": self.unit,
            "location_id": self.location_id,
            "warehouse_id": self.warehouse_id,
            "order_id": self.order_id,
            "outbound_time": self.outbound_time.strftime("%Y-%m-%d %H:%M:%S") if self.outbound_time else None,
            "operator_id": self.operator_id,
            "operator_name": self.operator_name,
            "created_time": self.created_time.strftime("%Y-%m-%d %H:%M:%S") if self.created_time else None
        }


class MaterialBoxInfo(Base):
    """料箱信息表"""
    __tablename__ = "material_box_info"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键")
    box_code = Column(String(50), unique=True, nullable=False, comment="料箱编号")
    box_type_id = Column(Integer, nullable=False, comment="料箱类型ID")
    warehouse_id = Column(Integer, nullable=True, comment="所属库房ID")
    location_id = Column(Integer, nullable=True, comment="库位ID")
    order_id = Column(Integer, nullable=True, comment="关联工单ID")
    capacity = Column(Integer, default=0, comment="容量")
    current_quantity = Column(Integer, default=0, comment="当前数量")
    status = Column(SmallInteger, default=1, comment="状态：0-空闲，1-使用中")
    created_time = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    def to_dict(self):
        return {
            "id": self.id,
            "box_code": self.box_code,
            "box_type_id": self.box_type_id,
            "warehouse_id": self.warehouse_id,
            "location_id": self.location_id,
            "order_id": self.order_id,
            "capacity": self.capacity,
            "current_quantity": self.current_quantity,
            "status": self.status,
            "created_time": self.created_time.strftime("%Y-%m-%d %H:%M:%S") if self.created_time else None
        }
