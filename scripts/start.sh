#!/bin/bash

# 仓储物资出入库动态管理系统 - 启动脚本
# 使用方法: ./scripts/start.sh

echo "=========================================="
echo "  仓储物资出入库动态管理系统 - 启动脚本"
echo "=========================================="
echo ""

# 进入项目根目录
cd "$(dirname "$0")/.."

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo "警告: .env 文件不存在，将使用默认配置"
fi

# 停止已存在的容器
echo ">>> 停止已存在的容器..."
docker-compose down 2>/dev/null

# 构建并启动服务
echo ">>> 构建并启动服务..."
docker-compose up -d --build

# 等待服务启动
echo ""
echo ">>> 等待服务启动..."
sleep 10

# 检查服务状态
echo ""
echo ">>> 服务状态:"
docker-compose ps

# 显示访问信息
echo ""
echo "=========================================="
echo "  系统启动完成!"
echo "=========================================="
echo ""
echo "访问地址:"
echo "  - 系统首页:    http://localhost"
echo "  - 前端服务:    http://localhost:3003"
echo "  - 后端API:     http://localhost:8003"
echo "  - API文档:     http://localhost:8003/docs"
echo "  - MySQL:       localhost:3307"
echo ""
echo "默认管理员账号:"
echo "  - 用户名: admin"
echo "  - 密码:   admin123"
echo ""
echo "日志查看:"
echo "  docker-compose logs -f [服务名]"
echo ""
echo "停止服务:"
echo "  ./scripts/stop.sh"
echo "=========================================="
