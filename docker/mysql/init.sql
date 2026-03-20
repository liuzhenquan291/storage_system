-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS warehouse_db DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE warehouse_db;

-- 用户表
CREATE TABLE IF NOT EXISTS sys_user (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键',
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
    password VARCHAR(255) NOT NULL COMMENT '密码',
    real_name VARCHAR(50) NOT NULL COMMENT '真实姓名',
    role_id INT DEFAULT NULL COMMENT '角色ID',
    warehouse_id INT DEFAULT NULL COMMENT '所属库房ID',
    phone VARCHAR(20) DEFAULT NULL COMMENT '联系电话',
    email VARCHAR(100) DEFAULT NULL COMMENT '邮箱',
    status TINYINT DEFAULT 1 COMMENT '状态：0-禁用，1-启用',
    deleted TINYINT DEFAULT 0 COMMENT '删除标记：0-未删除，1-已删除',
    created_by INT DEFAULT NULL COMMENT '创建人',
    created_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_by INT DEFAULT NULL COMMENT '更新人',
    updated_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_username (username),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统用户表';

-- 角色表
CREATE TABLE IF NOT EXISTS sys_role (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键',
    role_name VARCHAR(50) NOT NULL COMMENT '角色名称',
    role_code VARCHAR(50) NOT NULL UNIQUE COMMENT '角色编码',
    description VARCHAR(255) DEFAULT NULL COMMENT '描述',
    deleted TINYINT DEFAULT 0 COMMENT '删除标记：0-未删除，1-已删除',
    created_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_role_code (role_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统角色表';

-- 菜单表
CREATE TABLE IF NOT EXISTS sys_menu (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键',
    menu_name VARCHAR(50) NOT NULL COMMENT '菜单名称',
    menu_code VARCHAR(50) DEFAULT NULL COMMENT '菜单编码',
    parent_id INT DEFAULT 0 COMMENT '父菜单ID',
    menu_path VARCHAR(255) DEFAULT NULL COMMENT '路由路径',
    menu_icon VARCHAR(50) DEFAULT NULL COMMENT '图标',
    menu_type TINYINT DEFAULT 1 COMMENT '类型：0-目录，1-菜单，2-按钮',
    sort_order INT DEFAULT 0 COMMENT '排序',
    status TINYINT DEFAULT 1 COMMENT '状态：0-禁用，1-启用',
    created_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_parent_id (parent_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统菜单表';

-- 角色菜单关联表
CREATE TABLE IF NOT EXISTS sys_role_menu (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键',
    role_id INT NOT NULL COMMENT '角色ID',
    menu_id INT NOT NULL COMMENT '菜单ID',
    INDEX idx_role_id (role_id),
    INDEX idx_menu_id (menu_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='角色菜单关联表';

-- 库房信息表
CREATE TABLE IF NOT EXISTS warehouse_info (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键',
    warehouse_code VARCHAR(50) NOT NULL UNIQUE COMMENT '库房编号',
    warehouse_name VARCHAR(100) NOT NULL COMMENT '库房名称',
    description VARCHAR(255) DEFAULT NULL COMMENT '描述',
    address VARCHAR(255) DEFAULT NULL COMMENT '地址',
    status TINYINT DEFAULT 1 COMMENT '状态：0-停用，1-启用',
    created_by INT DEFAULT NULL COMMENT '创建人',
    created_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_warehouse_code (warehouse_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='库房信息表';

-- 产线信息表
CREATE TABLE IF NOT EXISTS production_line (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键',
    line_code VARCHAR(50) NOT NULL UNIQUE COMMENT '产线编号',
    line_name VARCHAR(100) NOT NULL COMMENT '产线名称',
    warehouse_id INT NOT NULL COMMENT '所属库房ID',
    description VARCHAR(255) DEFAULT NULL COMMENT '描述',
    status TINYINT DEFAULT 1 COMMENT '状态：0-停用，1-启用',
    created_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_line_code (line_code),
    INDEX idx_warehouse_id (warehouse_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='产线信息表';

-- 货架信息表
CREATE TABLE IF NOT EXISTS warehouse_shelf (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键',
    shelf_code VARCHAR(50) NOT NULL UNIQUE COMMENT '货架编号',
    shelf_no VARCHAR(50) DEFAULT NULL COMMENT '货架序号',
    shelf_name VARCHAR(100) NOT NULL COMMENT '货架名称',
    warehouse_id INT NOT NULL COMMENT '所属库房ID',
    line_id INT DEFAULT NULL COMMENT '所属产线ID',
    shelf_type TINYINT DEFAULT 1 COMMENT '货架类型：1-单伸位，2-双伸位',
    status TINYINT DEFAULT 1 COMMENT '状态：0-停用，1-启用',
    created_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_shelf_code (shelf_code),
    INDEX idx_warehouse_id (warehouse_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='货架信息表';

-- 库位信息表
CREATE TABLE IF NOT EXISTS warehouse_location (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键',
    location_code VARCHAR(50) NOT NULL UNIQUE COMMENT '库位编号',
    shelf_id INT NOT NULL COMMENT '所属货架ID',
    warehouse_id INT NOT NULL COMMENT '所属库房ID',
    line_id INT DEFAULT NULL COMMENT '所属产线ID',
    row_no INT DEFAULT NULL COMMENT '排号',
    col_no INT DEFAULT NULL COMMENT '列号',
    layer_no INT DEFAULT NULL COMMENT '层号',
    status TINYINT DEFAULT 1 COMMENT '状态：0-停用，1-启用，2-占用',
    created_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_location_code (location_code),
    INDEX idx_shelf_id (shelf_id),
    INDEX idx_warehouse_id (warehouse_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='库位信息表';

-- 物资类型表
CREATE TABLE IF NOT EXISTS material_type (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键',
    type_code VARCHAR(50) NOT NULL UNIQUE COMMENT '类型编码',
    type_name VARCHAR(100) NOT NULL COMMENT '类型名称',
    specification VARCHAR(255) DEFAULT NULL COMMENT '规格',
    unit VARCHAR(20) DEFAULT NULL COMMENT '单位',
    description VARCHAR(255) DEFAULT NULL COMMENT '描述',
    status TINYINT DEFAULT 1 COMMENT '状态：0-停用，1-启用',
    created_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_type_code (type_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='物资类型表';

-- 料箱类型表
CREATE TABLE IF NOT EXISTS material_box_type (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键',
    type_code VARCHAR(50) NOT NULL UNIQUE COMMENT '类型编码',
    type_name VARCHAR(100) NOT NULL COMMENT '类型名称',
    capacity INT DEFAULT 0 COMMENT '容量',
    description VARCHAR(255) DEFAULT NULL COMMENT '描述',
    created_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_type_code (type_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='料箱类型表';

-- 在库物资表
CREATE TABLE IF NOT EXISTS material_stock (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键',
    material_code VARCHAR(50) NOT NULL UNIQUE COMMENT '物资编号',
    material_name VARCHAR(100) NOT NULL COMMENT '物资名称',
    type_id INT NOT NULL COMMENT '物资类型ID',
    quantity INT DEFAULT 0 COMMENT '数量',
    unit VARCHAR(20) DEFAULT NULL COMMENT '单位',
    location_id INT DEFAULT NULL COMMENT '库位ID',
    warehouse_id INT DEFAULT NULL COMMENT '库房ID',
    batch_no VARCHAR(50) DEFAULT NULL COMMENT '批次号',
    status TINYINT DEFAULT 1 COMMENT '状态：1-在库',
    inbound_time DATETIME DEFAULT NULL COMMENT '入库时间',
    created_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_material_code (material_code),
    INDEX idx_type_id (type_id),
    INDEX idx_warehouse_id (warehouse_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='在库物资表';

-- 出库物资档案表
CREATE TABLE IF NOT EXISTS material_outbound_record (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键',
    material_code VARCHAR(50) NOT NULL COMMENT '物资编号',
    material_name VARCHAR(100) NOT NULL COMMENT '物资名称',
    type_id INT NOT NULL COMMENT '物资类型ID',
    quantity INT DEFAULT 0 COMMENT '出库数量',
    unit VARCHAR(20) DEFAULT NULL COMMENT '单位',
    location_id INT DEFAULT NULL COMMENT '原库位ID',
    warehouse_id INT DEFAULT NULL COMMENT '库房ID',
    order_id INT DEFAULT NULL COMMENT '出库工单ID',
    outbound_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '出库时间',
    operator_id INT DEFAULT NULL COMMENT '操作人ID',
    operator_name VARCHAR(50) DEFAULT NULL COMMENT '操作人姓名',
    created_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_material_code (material_code),
    INDEX idx_order_id (order_id),
    INDEX idx_outbound_time (outbound_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='出库物资档案表';

-- 料箱信息表
CREATE TABLE IF NOT EXISTS material_box_info (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键',
    box_code VARCHAR(50) NOT NULL UNIQUE COMMENT '料箱编号',
    box_type_id INT NOT NULL COMMENT '料箱类型ID',
    warehouse_id INT DEFAULT NULL COMMENT '所属库房ID',
    location_id INT DEFAULT NULL COMMENT '库位ID',
    order_id INT DEFAULT NULL COMMENT '关联工单ID',
    capacity INT DEFAULT 0 COMMENT '容量',
    current_quantity INT DEFAULT 0 COMMENT '当前数量',
    status TINYINT DEFAULT 1 COMMENT '状态：0-空闲，1-使用中',
    created_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_box_code (box_code),
    INDEX idx_warehouse_id (warehouse_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='料箱信息表';

-- 工单信息表
CREATE TABLE IF NOT EXISTS order_info (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键',
    order_code VARCHAR(50) NOT NULL UNIQUE COMMENT '工单号',
    order_type TINYINT NOT NULL COMMENT '工单类型：1-入库，2-出库，3-盘点',
    warehouse_id INT NOT NULL COMMENT '库房ID',
    line_id INT DEFAULT NULL COMMENT '产线ID',
    plan_quantity INT DEFAULT 0 COMMENT '计划数量',
    actual_quantity INT DEFAULT 0 COMMENT '实际数量',
    status TINYINT DEFAULT 0 COMMENT '状态：0-待执行，1-执行中，2-已完成，3-已取消',
    operator_id INT DEFAULT NULL COMMENT '操作人ID',
    operator_name VARCHAR(50) DEFAULT NULL COMMENT '操作人姓名',
    start_time DATETIME DEFAULT NULL COMMENT '开始时间',
    end_time DATETIME DEFAULT NULL COMMENT '完成时间',
    remark VARCHAR(500) DEFAULT NULL COMMENT '备注',
    deleted TINYINT DEFAULT 0 COMMENT '删除标记：0-未删除，1-已删除',
    created_by INT DEFAULT NULL COMMENT '创建人',
    created_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_order_code (order_code),
    INDEX idx_order_type (order_type),
    INDEX idx_status (status),
    INDEX idx_warehouse_id (warehouse_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='工单信息表';

-- 入库工单明细表
CREATE TABLE IF NOT EXISTS order_in_detail (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键',
    order_id INT NOT NULL COMMENT '工单ID',
    material_code VARCHAR(50) NOT NULL COMMENT '物资编号',
    material_name VARCHAR(100) NOT NULL COMMENT '物资名称',
    type_id INT NOT NULL COMMENT '物资类型ID',
    quantity INT DEFAULT 0 COMMENT '数量',
    unit VARCHAR(20) DEFAULT NULL COMMENT '单位',
    location_id INT DEFAULT NULL COMMENT '目标库位ID',
    batch_no VARCHAR(50) DEFAULT NULL COMMENT '批次号',
    created_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_order_id (order_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='入库工单明细表';

-- 出库工单明细表
CREATE TABLE IF NOT EXISTS order_out_detail (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键',
    order_id INT NOT NULL COMMENT '工单ID',
    material_code VARCHAR(50) NOT NULL COMMENT '物资编号',
    material_name VARCHAR(100) NOT NULL COMMENT '物资名称',
    type_id INT NOT NULL COMMENT '物资类型ID',
    quantity INT DEFAULT 0 COMMENT '出库数量',
    unit VARCHAR(20) DEFAULT NULL COMMENT '单位',
    location_id INT DEFAULT NULL COMMENT '原库位ID',
    stock_id INT DEFAULT NULL COMMENT '库存ID',
    created_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_order_id (order_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='出库工单明细表';

-- 盘点工单明细表
CREATE TABLE IF NOT EXISTS order_stock_detail (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键',
    order_id INT NOT NULL COMMENT '盘点工单ID',
    material_code VARCHAR(50) NOT NULL COMMENT '物资编号',
    material_name VARCHAR(100) NOT NULL COMMENT '物资名称',
    type_id INT NOT NULL COMMENT '物资类型ID',
    book_quantity INT DEFAULT 0 COMMENT '账面数量',
    actual_quantity INT DEFAULT 0 COMMENT '实际数量',
    difference INT DEFAULT 0 COMMENT '差异',
    location_id INT DEFAULT NULL COMMENT '库位ID',
    remark VARCHAR(255) DEFAULT NULL COMMENT '备注',
    created_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_order_id (order_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='盘点工单明细表';

-- 出入库记录表
CREATE TABLE IF NOT EXISTS order_inout_record (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键',
    order_id INT NOT NULL COMMENT '工单ID',
    order_code VARCHAR(50) NOT NULL COMMENT '工单号',
    order_type TINYINT NOT NULL COMMENT '工单类型',
    material_code VARCHAR(50) NOT NULL COMMENT '物资编号',
    material_name VARCHAR(100) NOT NULL COMMENT '物资名称',
    quantity INT DEFAULT 0 COMMENT '数量',
    operation_type TINYINT NOT NULL COMMENT '操作类型：1-入库，2-出库',
    before_quantity INT DEFAULT 0 COMMENT '操作前数量',
    after_quantity INT DEFAULT 0 COMMENT '操作后数量',
    operator_id INT DEFAULT NULL COMMENT '操作人ID',
    operator_name VARCHAR(50) DEFAULT NULL COMMENT '操作人姓名',
    operation_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间',
    warehouse_id INT DEFAULT NULL COMMENT '库房ID',
    location_id INT DEFAULT NULL COMMENT '库位ID',
    created_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_order_id (order_id),
    INDEX idx_operation_type (operation_type),
    INDEX idx_operation_time (operation_time),
    INDEX idx_operator_id (operator_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='出入库记录表';

-- 设备类型表
CREATE TABLE IF NOT EXISTS device_type (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键',
    type_code VARCHAR(50) NOT NULL UNIQUE COMMENT '类型编码',
    type_name VARCHAR(100) NOT NULL COMMENT '类型名称',
    description VARCHAR(255) DEFAULT NULL COMMENT '描述',
    created_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_type_code (type_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='设备类型表';

-- 设备信息表
CREATE TABLE IF NOT EXISTS device_info (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键',
    device_code VARCHAR(50) NOT NULL UNIQUE COMMENT '设备编号',
    device_name VARCHAR(100) NOT NULL COMMENT '设备名称',
    type_id INT NOT NULL COMMENT '设备类型ID',
    line_id INT DEFAULT NULL COMMENT '所属产线ID',
    warehouse_id INT DEFAULT NULL COMMENT '所属库房ID',
    ip_address VARCHAR(50) DEFAULT NULL COMMENT 'IP地址',
    port INT DEFAULT NULL COMMENT '端口',
    status TINYINT DEFAULT 0 COMMENT '状态：0-离线，1-在线',
    description VARCHAR(255) DEFAULT NULL COMMENT '描述',
    created_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_device_code (device_code),
    INDEX idx_warehouse_id (warehouse_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='设备信息表';

-- IOT设备表
CREATE TABLE IF NOT EXISTS device_iot (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键',
    device_code VARCHAR(50) NOT NULL UNIQUE COMMENT '设备编号',
    device_name VARCHAR(100) NOT NULL COMMENT '设备名称',
    device_type TINYINT NOT NULL COMMENT '设备类型：1-摄像头，2-温湿度传感器，3-大屏',
    ip_address VARCHAR(50) DEFAULT NULL COMMENT 'IP地址',
    port INT DEFAULT NULL COMMENT '端口',
    warehouse_id INT DEFAULT NULL COMMENT '所属库房ID',
    status TINYINT DEFAULT 0 COMMENT '状态：0-离线，1-在线',
    description VARCHAR(255) DEFAULT NULL COMMENT '描述',
    created_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_device_code (device_code),
    INDEX idx_warehouse_id (warehouse_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='IOT设备表';

-- 操作日志表
CREATE TABLE IF NOT EXISTS sys_operation_log (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键',
    user_id INT DEFAULT NULL COMMENT '操作用户ID',
    username VARCHAR(50) DEFAULT NULL COMMENT '操作用户名',
    operation_type VARCHAR(50) DEFAULT NULL COMMENT '操作类型',
    operation_desc VARCHAR(500) DEFAULT NULL COMMENT '操作描述',
    request_method VARCHAR(10) DEFAULT NULL COMMENT '请求方法',
    request_url VARCHAR(255) DEFAULT NULL COMMENT '请求URL',
    request_params TEXT DEFAULT NULL COMMENT '请求参数',
    response_result TEXT DEFAULT NULL COMMENT '响应结果',
    ip_address VARCHAR(50) DEFAULT NULL COMMENT 'IP地址',
    operation_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间',
    created_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_user_id (user_id),
    INDEX idx_operation_time (operation_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='操作日志表';

-- 系统运行日志表
CREATE TABLE IF NOT EXISTS sys_run_log (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键',
    log_level VARCHAR(20) NOT NULL COMMENT '日志级别',
    log_content TEXT DEFAULT NULL COMMENT '日志内容',
    log_source VARCHAR(100) DEFAULT NULL COMMENT '日志来源',
    created_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_log_level (log_level),
    INDEX idx_created_time (created_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统运行日志表';
