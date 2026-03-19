# 仓储物资出入库动态管理系统

一个用于管理仓储物资出入库业务的综合性系统，支持库房管理、物资管理、工单管理、设备管理等核心功能。

## 功能模块

- **用户权限管理**：用户管理、角色管理、菜单管理
- **库房管理**：库房、产线、货架、库位管理
- **物资管理**：物资类型、在库物资、出库记录、料箱管理
- **工单管理**：入库任务、出库任务、盘点任务、出入库记录
- **设备管理**：设备类型、设备信息、IOT设备管理
- **系统监控**：仪表盘、操作日志、系统运行日志

## 技术栈

### 后端
- Python 3.11 + FastAPI
- SQLAlchemy 2.0
- MySQL 8.0
- JWT 认证

### 前端
- Vue 3 + Composition API
- Element Plus
- Pinia
- Axios

### 部署
- Docker + Docker Compose
- Nginx 反向代理

## 端口配置

| 服务 | 端口 |
|------|------|
| MySQL | 3307 |
| 后端 API | 8003 |
| 前端 | 3003 |
| Nginx | 80 |

## 快速开始

### 1. 启动服务

```bash
./scripts/start.sh
```

### 2. 访问系统

- 系统首页: http://localhost
- API 文档: http://localhost:8003/docs

### 3. 默认管理员账号

- 用户名: `admin`
- 密码: `admin123`

## 常用命令

```bash
# 启动服务
./scripts/start.sh

# 停止服务
./scripts/stop.sh

# 重启服务
./scripts/restart.sh

# 查看日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
```

## 目录结构

```
.
├── backend/                    # 后端代码
│   ├── app/
│   │   ├── api/               # API 路由
│   │   ├── core/              # 核心配置
│   │   ├── models/            # 数据模型
│   │   ├── schemas/           # Pydantic 模型
│   │   ├── services/          # 业务逻辑
│   │   └── middleware/        # 中间件
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                   # 前端代码
│   ├── src/
│   │   ├── api/               # API 接口
│   │   ├── views/             # 页面组件
│   │   ├── components/        # 公共组件
│   │   ├── store/             # 状态管理
│   │   ├── router/            # 路由配置
│   │   └── utils/             # 工具函数
│   ├── package.json
│   └── Dockerfile
├── docker/                     # Docker 配置
│   ├── mysql/
│   │   └── init.sql           # 数据库初始化
│   └── nginx/
│       └── nginx.conf         # Nginx 配置
├── scripts/                    # 脚本
│   ├── start.sh
│   ├── stop.sh
│   └── restart.sh
├── docker-compose.yml
├── .env
└── README.md
```

## 环境变量配置

在 `.env` 文件中配置：

```env
# MySQL
MYSQL_ROOT_PASSWORD=root123
MYSQL_DATABASE=warehouse_db
MYSQL_USER=warehouse
MYSQL_PASSWORD=warehouse123

# Admin
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123

# Ports
MYSQL_PORT=3307
BACKEND_PORT=8003
FRONTEND_PORT=3003
NGINX_PORT=80
```

## 数据持久化

MySQL 数据存储在 Docker Volume `mysql_data` 中，确保数据在容器重启后不丢失。

备份命令：
```bash
docker exec warehouse_mysql mysqldump -u root -proot123 warehouse_db > backup.sql
```

## 许可证

MIT License
