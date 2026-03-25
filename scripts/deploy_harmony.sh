#!/bin/bash
#
# 鸿蒙系统 / 银河麒麟 ARM64 部署脚本
# 适用于：麒麟 V10 SP1 + 华为麒麟990 (aarch64)
#

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

log_info "====================================="
log_info "  仓储物资管理系统 - 鸿蒙系统部署"
log_info "====================================="
log_info "项目路径: $PROJECT_DIR"
echo ""

# ====================
# 1. 检查系统环境
# ====================
log_info "步骤 1/8: 检查系统环境..."

# 检查架构
ARCH=$(uname -m)
log_info "系统架构: $ARCH"

if [ "$ARCH" != "aarch64" ] && [ "$ARCH" != "arm64" ]; then
    log_warn "当前架构为 $ARCH，本脚本主要为 ARM64 (aarch64) 优化"
    read -p "是否继续部署? (y/n): " confirm
    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
        exit 1
    fi
fi

# 检查 apt-get
if ! command -v apt-get &> /dev/null; then
    log_error "系统不支持 apt-get 包管理器"
    exit 1
fi

log_success "系统环境检查通过"

# ====================
# 2. 检查并安装 Python
# ====================
log_info "步骤 2/8: 检查 Python 环境..."

if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
    log_info "检测到 Python $PYTHON_VERSION"
    
    # 检查版本是否 >= 3.8
    if [ "$(printf '%s\n' "3.8" "$PYTHON_VERSION" | sort -V | head -n1)" = "3.8" ]; then
        log_success "Python 版本符合要求"
    else
        log_warn "Python 版本过低，建议安装 3.8+"
        log_info "尝试安装 Python 3.8..."
        sudo apt-get update
        sudo apt-get install -y python3.8 python3.8-venv python3.8-pip
    fi
else
    log_info "安装 Python 3.8..."
    sudo apt-get update
    sudo apt-get install -y python3 python3-venv python3-pip
fi

# 检查 pip
if ! command -v pip3 &> /dev/null; then
    log_info "安装 pip3..."
    sudo apt-get install -y python3-pip
fi

PYTHON_CMD=$(command -v python3)
log_success "Python 就绪: $PYTHON_CMD"

# ====================
# 3. 检查并安装 Node.js
# ====================
log_info "步骤 3/8: 检查 Node.js 环境..."

if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version | grep -oP '\d+' | head -n1)
    log_info "检测到 Node.js $(node --version)"
    
    if [ "$NODE_VERSION" -ge 16 ]; then
        log_success "Node.js 版本符合要求"
    else
        log_warn "Node.js 版本过低，建议升级至 16.x"
        read -p "是否升级 Node.js? (y/n): " upgrade_node
        if [ "$upgrade_node" = "y" ] || [ "$upgrade_node" = "Y" ]; then
            log_info "升级 Node.js 16.x..."
            curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
            sudo apt-get install -y nodejs
        fi
    fi
else
    log_info "安装 Node.js 16.x..."
    curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
    sudo apt-get install -y nodejs
fi

log_success "Node.js 就绪: $(node --version)"

# ====================
# 4. 创建 Python 虚拟环境
# ====================
log_info "步骤 4/8: 创建 Python 虚拟环境..."

BACKEND_DIR="$PROJECT_DIR/backend"
VENV_DIR="$BACKEND_DIR/venv"

if [ -d "$VENV_DIR" ]; then
    log_warn "虚拟环境已存在，是否重新创建?"
    read -p "重新创建? (y/n): " recreate
    if [ "$recreate" = "y" ] || [ "$recreate" = "Y" ]; then
        rm -rf "$VENV_DIR"
        $PYTHON_CMD -m venv "$VENV_DIR"
        log_success "虚拟环境已重新创建"
    fi
else
    $PYTHON_CMD -m venv "$VENV_DIR"
    log_success "虚拟环境已创建"
fi

# 激活虚拟环境
source "$VENV_DIR/bin/activate"
log_info "虚拟环境已激活"

# 配置 pip 国内源（清华）
log_info "配置 pip 使用清华源..."
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
pip config set install.trusted-host pypi.tuna.tsinghua.edu.cn

# 升级 pip
pip install --upgrade pip

# ====================
# 5. 安装后端依赖
# ====================
log_info "步骤 5/8: 安装后端依赖..."

cd "$BACKEND_DIR"
pip install -r requirements.txt

log_success "后端依赖安装完成"

# ====================
# 6. 安装前端依赖
# ====================
log_info "步骤 6/8: 安装前端依赖..."

FRONTEND_DIR="$PROJECT_DIR/frontend"
cd "$FRONTEND_DIR"

# 配置 npm 国内镜像（淘宝）
log_info "配置 npm 使用淘宝镜像..."
npm config set registry https://registry.npmmirror.com

# 检查 node_modules
if [ -d "node_modules" ]; then
    log_warn "node_modules 已存在"
    read -p "是否重新安装前端依赖? (y/n): " reinstall
    if [ "$reinstall" = "y" ] || [ "$reinstall" = "Y" ]; then
        rm -rf node_modules package-lock.json
        npm install
    fi
else
    npm install
fi

log_success "前端依赖安装完成"

# ====================
# 7. 配置环境变量
# ====================
log_info "步骤 7/8: 配置环境变量..."

ENV_FILE="$PROJECT_DIR/.env"

# 生成随机 JWT 密钥
JWT_SECRET=$(openssl rand -hex 32 2>/dev/null || head -c 64 /dev/urandom | xxd -p | tr -d '\n' | head -c 64)

# 检查 .env 文件是否存在
if [ -f "$ENV_FILE" ]; then
    log_info "检测到已存在的 .env 文件"
    
    # 检查是否已配置 SQLite
    if grep -q "DB_TYPE=sqlite" "$ENV_FILE"; then
        log_success ".env 已配置为 SQLite，跳过配置步骤"
        create_env=false
    else
        log_warn ".env 使用的是 MySQL 配置，需要切换为 SQLite"
        read -p "是否自动修改为 SQLite 配置? (y/n) [默认: y]: " convert_sqlite
        convert_sqlite=${convert_sqlite:-y}
        
        if [ "$convert_sqlite" = "y" ] || [ "$convert_sqlite" = "Y" ]; then
            # 读取现有配置
            ADMIN_USERNAME=$(grep "^ADMIN_USERNAME=" "$ENV_FILE" | cut -d= -f2 || echo "admin")
            ADMIN_PASSWORD=$(grep "^ADMIN_PASSWORD=" "$ENV_FILE" | cut -d= -f2 || echo "admin123")
            ADMIN_REAL_NAME=$(grep "^ADMIN_REAL_NAME=" "$ENV_FILE" | cut -d= -f2 || echo "系统管理员")
            
            # 备份原配置
            cp "$ENV_FILE" "$ENV_FILE.bak.$(date +%Y%m%d%H%M%S)"
            
            # 重写为 SQLite 配置
            cat > "$ENV_FILE" << EOF
# 数据库配置 (SQLite)
DB_TYPE=sqlite
SQLITE_PATH=./warehouse.db

# JWT 配置
JWT_SECRET=$JWT_SECRET
JWT_ALGORITHM=HS256
JWT_EXPIRE_HOURS=2

# 管理员配置
ADMIN_USERNAME=${ADMIN_USERNAME:-admin}
ADMIN_PASSWORD=${ADMIN_PASSWORD:-admin123}
ADMIN_REAL_NAME=${ADMIN_REAL_NAME:-系统管理员}

# 端口配置
BACKEND_PORT=8003
FRONTEND_PORT=3003
EOF
            log_success ".env 已更新为 SQLite 配置，原配置已备份"
            create_env=false
        else
            log_warn "保留 MySQL 配置，但鸿蒙部署需要 SQLite"
            log_info "请手动修改 .env，添加: DB_TYPE=sqlite 和 SQLITE_PATH=./warehouse.db"
            read -p "按回车继续..."
        fi
    fi
else
    create_env=true
fi

if [ "$create_env" = true ]; then
    log_info "创建 .env 配置文件..."
    
    read -p "设置管理员账号 [默认: admin]: " admin_username
    admin_username=${admin_username:-admin}
    
    read -s -p "设置管理员密码 [默认: admin123]: " admin_password
    echo
    admin_password=${admin_password:-admin123}
    
    read -p "设置管理员昵称 [默认: 系统管理员]: " admin_realname
    admin_realname=${admin_realname:-系统管理员}
    
    # 创建 .env 文件 - 使用 SQLite
    cat > "$ENV_FILE" << EOF
# 数据库配置 (SQLite)
DB_TYPE=sqlite
SQLITE_PATH=./warehouse.db

# JWT 配置
JWT_SECRET=$JWT_SECRET
JWT_ALGORITHM=HS256
JWT_EXPIRE_HOURS=2

# 管理员配置
ADMIN_USERNAME=$admin_username
ADMIN_PASSWORD=$admin_password
ADMIN_REAL_NAME=$admin_realname

# 端口配置
BACKEND_PORT=8003
FRONTEND_PORT=3003
EOF

    log_success ".env 文件已创建"
fi

# ====================
# 8. 初始化数据库
# ====================
log_info "步骤 8/8: 初始化数据库..."

cd "$BACKEND_DIR"

# 设置环境变量
export DB_TYPE=sqlite
export SQLITE_PATH="./warehouse.db"

# 运行初始化脚本
log_info "创建数据库表..."
python3 << 'PYTHON_EOF'
import asyncio
import sys
sys.path.insert(0, '.')

from app.core.database import sync_engine, Base
from app.models import user, warehouse, material, order, device

# 创建所有表
Base.metadata.create_all(bind=sync_engine)
print("数据库表创建成功")
PYTHON_EOF

# 初始化管理员账号
log_info "初始化管理员账号..."
python3 << 'PYTHON_EOF'
import asyncio
import sys
import os
sys.path.insert(0, '.')

from app.core.config import settings
from app.core.security import get_password_hash
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# 创建同步引擎
db_url = settings.DATABASE_URL.replace("+aiosqlite", "")
engine = create_engine(db_url, connect_args={"check_same_thread": False})
Session = sessionmaker(bind=engine)
session = Session()

try:
    # 检查管理员是否已存在
    result = session.execute(text("SELECT id FROM users WHERE username = :username"), {"username": settings.ADMIN_USERNAME})
    if result.fetchone():
        print(f"管理员账号 '{settings.ADMIN_USERNAME}' 已存在")
    else:
        # 创建管理员
        hashed_password = get_password_hash(settings.ADMIN_PASSWORD)
        session.execute(text("""
            INSERT INTO users (username, password, real_name, role, is_active, created_at)
            VALUES (:username, :password, :real_name, 'admin', 1, datetime('now'))
        """), {
            "username": settings.ADMIN_USERNAME,
            "password": hashed_password,
            "real_name": settings.ADMIN_REAL_NAME
        })
        session.commit()
        print(f"管理员账号 '{settings.ADMIN_USERNAME}' 创建成功")
except Exception as e:
    print(f"初始化管理员失败: {e}")
    session.rollback()
finally:
    session.close()
PYTHON_EOF

log_success "数据库初始化完成"

# ====================
# 9. 创建 Systemd 服务
# ====================
log_info "创建 Systemd 服务..."

# 创建日志目录
mkdir -p "$PROJECT_DIR/logs"

# 后端服务
BACKEND_SERVICE="/etc/systemd/system/warehouse-backend.service"
sudo tee "$BACKEND_SERVICE" > /dev/null << EOF
[Unit]
Description=Warehouse Backend Service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_DIR/backend
Environment="PATH=$PROJECT_DIR/backend/venv/bin"
Environment="DB_TYPE=sqlite"
Environment="SQLITE_PATH=$PROJECT_DIR/backend/warehouse.db"
EnvironmentFile=$PROJECT_DIR/.env
ExecStart=$PROJECT_DIR/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8003
Restart=always
RestartSec=5
StandardOutput=append:$PROJECT_DIR/logs/backend.log
StandardError=append:$PROJECT_DIR/logs/backend-error.log

[Install]
WantedBy=multi-user.target
EOF

# 前端服务
FRONTEND_SERVICE="/etc/systemd/system/warehouse-frontend.service"
sudo tee "$FRONTEND_SERVICE" > /dev/null << EOF
[Unit]
Description=Warehouse Frontend Service
After=network.target warehouse-backend.service
Requires=warehouse-backend.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_DIR/frontend
ExecStart=/usr/bin/npm run dev
Restart=always
RestartSec=5
StandardOutput=append:$PROJECT_DIR/logs/frontend.log
StandardError=append:$PROJECT_DIR/logs/frontend-error.log

[Install]
WantedBy=multi-user.target
EOF

# 重新加载 systemd
sudo systemctl daemon-reload

# 启用开机自启
sudo systemctl enable warehouse-backend.service
sudo systemctl enable warehouse-frontend.service

log_success "Systemd 服务已创建"

# 创建管理脚本
MANAGE_SCRIPT="$PROJECT_DIR/manage.sh"
cat > "$MANAGE_SCRIPT" << 'MEOF'
#!/bin/bash
#
# 仓储系统服务管理脚本
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

show_help() {
    echo "用法: ./manage.sh [命令]"
    echo ""
    echo "命令:"
    echo "  start     启动服务"
    echo "  stop      停止服务"
    echo "  restart   重启服务"
    echo "  status    查看状态"
    echo "  logs      查看日志"
    echo "  enable    设置开机自启"
    echo "  disable   取消开机自启"
}

case "$1" in
    start)
        echo -e "${GREEN}启动服务...${NC}"
        sudo systemctl start warehouse-backend
        sudo systemctl start warehouse-frontend
        echo -e "${GREEN}服务已启动${NC}"
        echo "  后端: http://localhost:8003"
        echo "  前端: http://localhost:3003"
        ;;
    stop)
        echo -e "${YELLOW}停止服务...${NC}"
        sudo systemctl stop warehouse-frontend
        sudo systemctl stop warehouse-backend
        echo -e "${GREEN}服务已停止${NC}"
        ;;
    restart)
        echo -e "${YELLOW}重启服务...${NC}"
        sudo systemctl restart warehouse-backend
        sudo systemctl restart warehouse-frontend
        echo -e "${GREEN}服务已重启${NC}"
        ;;
    status)
        echo -e "${BLUE}服务状态:${NC}"
        echo ""
        echo "后端服务:"
        sudo systemctl status warehouse-backend --no-pager -l
        echo ""
        echo "前端服务:"
        sudo systemctl status warehouse-frontend --no-pager -l
        ;;
    logs)
        echo -e "${BLUE}查看日志 (按 Ctrl+C 退出):${NC}"
        echo ""
        tail -f "$SCRIPT_DIR/logs/"*.log 2>/dev/null
        ;;
    enable)
        sudo systemctl enable warehouse-backend
        sudo systemctl enable warehouse-frontend
        echo -e "${GREEN}已设置开机自启${NC}"
        ;;
    disable)
        sudo systemctl disable warehouse-backend
        sudo systemctl disable warehouse-frontend
        echo -e "${YELLOW}已取消开机自启${NC}"
        ;;
    *)
        show_help
        ;;
esac
MEOF

chmod +x "$MANAGE_SCRIPT"
log_success "管理脚本已创建: $MANAGE_SCRIPT"

# ====================
# 部署完成
# ====================
echo ""
echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}      部署完成!                    ${NC}"
echo -e "${GREEN}=====================================${NC}"
echo ""
echo "部署信息:"
echo "  项目路径: $PROJECT_DIR"
echo "  数据库: SQLite ($PROJECT_DIR/backend/warehouse.db)"
echo "  后端端口: 8003"
echo "  前端端口: 3003"
echo "  日志路径: $PROJECT_DIR/logs/"
echo ""
echo "服务管理命令:"
echo "  cd $PROJECT_DIR"
echo "  ./manage.sh start     # 启动服务"
echo "  ./manage.sh stop      # 停止服务"
echo "  ./manage.sh restart   # 重启服务"
echo "  ./manage.sh status    # 查看状态"
echo "  ./manage.sh logs      # 查看日志"
echo "  ./manage.sh enable    # 设置开机自启"
echo "  ./manage.sh disable   # 取消开机自启"
echo ""
echo "Systemd 命令:"
echo "  sudo systemctl start warehouse-backend    # 启动后端"
echo "  sudo systemctl start warehouse-frontend   # 启动前端"
echo "  sudo systemctl stop warehouse-backend     # 停止后端"
echo "  sudo systemctl stop warehouse-frontend    # 停止前端"
echo ""
echo "访问地址:"
echo "  后端 API: http://localhost:8003"
echo "  前端页面: http://localhost:3003"
echo "  API 文档: http://localhost:8003/docs"
echo ""

# 是否立即启动
read -p "是否立即启动服务? (y/n): " start_now
if [ "$start_now" = "y" ] || [ "$start_now" = "Y" ]; then
    echo ""
    sudo systemctl start warehouse-backend
    sudo systemctl start warehouse-frontend
    log_success "服务已启动"
    echo "  后端: http://localhost:8003"
    echo "  前端: http://localhost:3003"
fi
