"""
工单相关模型
"""
from sqlalchemy import Column, Integer, String, SmallInteger, DateTime, Text
from datetime import datetime

from app.core.database import Base


class OrderInfo(Base):
    """工单信息表"""
    __tablename__ = "order_info"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键")
    order_code = Column(String(50), unique=True, nullable=False, comment="工单号")
    order_type = Column(SmallInteger, nullable=False, comment="工单类型：1-入库，2-出库，3-盘点")
    warehouse_id = Column(Integer, nullable=False, comment="库房ID")
    line_id = Column(Integer, nullable=True, comment="产线ID")
    plan_quantity = Column(Integer, default=0, comment="计划数量")
    actual_quantity = Column(Integer, default=0, comment="实际数量")
    status = Column(SmallInteger, default=0, comment="状态：0-待执行，1-执行中，2-已完成，3-已取消")
    operator_id = Column(Integer, nullable=True, comment="操作人ID")
    operator_name = Column(String(50), nullable=True, comment="操作人姓名")
    start_time = Column(DateTime, nullable=True, comment="开始时间")
    end_time = Column(DateTime, nullable=True, comment="完成时间")
    remark = Column(String(500), nullable=True, comment="备注")
    deleted = Column(SmallInteger, default=0, comment="删除标记：0-未删除，1-已删除")
    created_by = Column(Integer, nullable=True, comment="创建人")
    created_time = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    def to_dict(self):
        return {
            "id": self.id,
            "order_code": self.order_code,
            "order_type": self.order_type,
            "warehouse_id": self.warehouse_id,
            "line_id": self.line_id,
            "plan_quantity": self.plan_quantity,
            "actual_quantity": self.actual_quantity,
            "status": self.status,
            "operator_id": self.operator_id,
            "operator_name": self.operator_name,
            "start_time": self.start_time.strftime("%Y-%m-%d %H:%M:%S") if self.start_time else None,
            "end_time": self.end_time.strftime("%Y-%m-%d %H:%M:%S") if self.end_time else None,
            "remark": self.remark,
            "created_time": self.created_time.strftime("%Y-%m-%d %H:%M:%S") if self.created_time else None
        }


class OrderInDetail(Base):
    """入库工单明细表"""
    __tablename__ = "order_in_detail"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键")
    order_id = Column(Integer, nullable=False, comment="工单ID")
    material_code = Column(String(50), nullable=False, comment="物资编号")
    material_name = Column(String(100), nullable=False, comment="物资名称")
    type_id = Column(Integer, nullable=False, comment="物资类型ID")
    quantity = Column(Integer, default=0, comment="数量")
    unit = Column(String(20), nullable=True, comment="单位")
    location_id = Column(Integer, nullable=True, comment="目标库位ID")
    batch_no = Column(String(50), nullable=True, comment="批次号")
    created_time = Column(DateTime, default=datetime.now, comment="创建时间")
    
    def to_dict(self):
        return {
            "id": self.id,
            "order_id": self.order_id,
            "material_code": self.material_code,
            "material_name": self.material_name,
            "type_id": self.type_id,
            "quantity": self.quantity,
            "unit": self.unit,
            "location_id": self.location_id,
            "batch_no": self.batch_no,
            "created_time": self.created_time.strftime("%Y-%m-%d %H:%M:%S") if self.created_time else None
        }


class OrderOutDetail(Base):
    """出库工单明细表"""
    __tablename__ = "order_out_detail"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键")
    order_id = Column(Integer, nullable=False, comment="工单ID")
    material_code = Column(String(50), nullable=False, comment="物资编号")
    material_name = Column(String(100), nullable=False, comment="物资名称")
    type_id = Column(Integer, nullable=False, comment="物资类型ID")
    quantity = Column(Integer, default=0, comment="出库数量")
    unit = Column(String(20), nullable=True, comment="单位")
    location_id = Column(Integer, nullable=True, comment="原库位ID")
    stock_id = Column(Integer, nullable=True, comment="库存ID")
    created_time = Column(DateTime, default=datetime.now, comment="创建时间")
    
    def to_dict(self):
        return {
            "id": self.id,
            "order_id": self.order_id,
            "material_code": self.material_code,
            "material_name": self.material_name,
            "type_id": self.type_id,
            "quantity": self.quantity,
            "unit": self.unit,
            "location_id": self.location_id,
            "stock_id": self.stock_id,
            "created_time": self.created_time.strftime("%Y-%m-%d %H:%M:%S") if self.created_time else None
        }


class OrderStockDetail(Base):
    """盘点工单明细表"""
    __tablename__ = "order_stock_detail"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键")
    order_id = Column(Integer, nullable=False, comment="盘点工单ID")
    material_code = Column(String(50), nullable=False, comment="物资编号")
    material_name = Column(String(100), nullable=False, comment="物资名称")
    type_id = Column(Integer, nullable=False, comment="物资类型ID")
    book_quantity = Column(Integer, default=0, comment="账面数量")
    actual_quantity = Column(Integer, default=0, comment="实际数量")
    difference = Column(Integer, default=0, comment="差异")
    location_id = Column(Integer, nullable=True, comment="库位ID")
    remark = Column(String(255), nullable=True, comment="备注")
    created_time = Column(DateTime, default=datetime.now, comment="创建时间")
    
    def to_dict(self):
        return {
            "id": self.id,
            "order_id": self.order_id,
            "material_code": self.material_code,
            "material_name": self.material_name,
            "type_id": self.type_id,
            "book_quantity": self.book_quantity,
            "actual_quantity": self.actual_quantity,
            "difference": self.difference,
            "location_id": self.location_id,
            "remark": self.remark,
            "created_time": self.created_time.strftime("%Y-%m-%d %H:%M:%S") if self.created_time else None
        }


class OrderInoutRecord(Base):
    """出入库记录表"""
    __tablename__ = "order_inout_record"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键")
    order_id = Column(Integer, nullable=False, comment="工单ID")
    order_code = Column(String(50), nullable=False, comment="工单号")
    order_type = Column(SmallInteger, nullable=False, comment="工单类型")
    material_code = Column(String(50), nullable=False, comment="物资编号")
    material_name = Column(String(100), nullable=False, comment="物资名称")
    quantity = Column(Integer, default=0, comment="数量")
    operation_type = Column(SmallInteger, nullable=False, comment="操作类型：1-入库，2-出库")
    before_quantity = Column(Integer, default=0, comment="操作前数量")
    after_quantity = Column(Integer, default=0, comment="操作后数量")
    operator_id = Column(Integer, nullable=True, comment="操作人ID")
    operator_name = Column(String(50), nullable=True, comment="操作人姓名")
    operation_time = Column(DateTime, default=datetime.now, comment="操作时间")
    warehouse_id = Column(Integer, nullable=True, comment="库房ID")
    location_id = Column(Integer, nullable=True, comment="库位ID")
    created_time = Column(DateTime, default=datetime.now, comment="创建时间")
    
    def to_dict(self):
        return {
            "id": self.id,
            "order_id": self.order_id,
            "order_code": self.order_code,
            "order_type": self.order_type,
            "material_code": self.material_code,
            "material_name": self.material_name,
            "quantity": self.quantity,
            "operation_type": self.operation_type,
            "before_quantity": self.before_quantity,
            "after_quantity": self.after_quantity,
            "operator_id": self.operator_id,
            "operator_name": self.operator_name,
            "operation_time": self.operation_time.strftime("%Y-%m-%d %H:%M:%S") if self.operation_time else None,
            "warehouse_id": self.warehouse_id,
            "location_id": self.location_id,
            "created_time": self.created_time.strftime("%Y-%m-%d %H:%M:%S") if self.created_time else None
        }
