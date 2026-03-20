#!/bin/bash

# 仓储物资出入库动态管理系统 - 启动脚本
# 支持 Windows (Git Bash/WSL) 和 Linux/Mac

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# 检查 Docker 是否安装
check_docker() {
    print_info "检查 Docker 安装状态..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker 未安装！"
        echo ""
        echo "请按以下步骤安装 Docker："
        echo "1. Windows: 访问 https://docs.docker.com/desktop/install/windows-install/"
        echo "2. Mac: 访问 https://docs.docker.com/desktop/install/mac-install/"
        echo "3. Linux: 运行 sudo apt-get install docker.io docker-compose"
        echo ""
        echo "安装完成后，请重新运行此脚本。"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose 未安装！"
        echo "Docker Desktop 已包含 Docker Compose。"
        echo "如果是 Linux，请安装 docker-compose-plugin。"
        exit 1
    fi
    
    # 检查 Docker 是否正在运行
    if ! docker info &> /dev/null; then
        print_error "Docker 未运行！"
        echo "请启动 Docker Desktop 或运行 sudo systemctl start docker"
        exit 1
    fi
    
    print_success "Docker 和 Docker Compose 已安装且运行正常"
    echo ""
}

# 选择数据存放路径
select_data_path() {
    print_info "选择数据存放路径"
    echo ""
    echo "请选择数据存放位置（包含数据库数据、日志等）："
    echo ""
    
    # 默认路径
    DEFAULT_PATH="$HOME/warehouse_data"
    
    # 在 Windows 环境下使用不同的默认路径
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "win32" ]]; then
        DEFAULT_PATH="$USERPROFILE/warehouse_data"
    fi
    
    echo "默认路径: $DEFAULT_PATH"
    echo ""
    read -p "使用默认路径？(Y/n): " use_default
    
    if [[ "$use_default" =~ ^[Nn]$ ]]; then
        read -p "请输入新的数据存放路径: " DATA_PATH
        # 去除路径两端的引号
        DATA_PATH=$(echo "$DATA_PATH" | sed 's/^["'"'"']*//;s/["'"'"']*$//')
    else
        DATA_PATH="$DEFAULT_PATH"
    fi
    
    # 创建目录
    mkdir -p "$DATA_PATH"
    
    print_success "数据将存放在: $DATA_PATH"
    echo ""
}

# 设置 .env 文件
setup_env() {
    print_info "配置系统参数"
    echo ""
    
    ENV_FILE=".env"
    
    # 如果 .env 已存在，询问是否覆盖
    if [ -f "$ENV_FILE" ]; then
        read -p ".env 文件已存在，是否重新配置？(y/N): " reconfig
        if [[ ! "$reconfig" =~ ^[Yy]$ ]]; then
            print_info "使用现有的 .env 配置"
            return
        fi
    fi
    
    echo "=== 数据库配置 ==="
    echo ""
    
    # MySQL ROOT 密码
    read -sp "设置 MySQL ROOT 密码 (默认: root123): " MYSQL_ROOT_PASSWORD
    echo ""
    MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD:-root123}
    
    # 普通用户配置
    read -p "设置数据库普通用户名 (默认: warehouse): " MYSQL_USER
    MYSQL_USER=${MYSQL_USER:-warehouse}
    
    read -sp "设置数据库普通用户密码 (默认: warehouse123): " MYSQL_PASSWORD
    echo ""
    MYSQL_PASSWORD=${MYSQL_PASSWORD:-warehouse123}
    
    echo ""
    echo "=== 管理员账号配置 ==="
    echo ""
    
    read -p "设置管理员用户名 (默认: admin): " ADMIN_USERNAME
    ADMIN_USERNAME=${ADMIN_USERNAME:-admin}
    
    read -sp "设置管理员密码 (默认: admin123): " ADMIN_PASSWORD
    echo ""
    ADMIN_PASSWORD=${ADMIN_PASSWORD:-admin123}
    
    read -p "设置管理员昵称 (默认: 系统管理员): " ADMIN_REAL_NAME
    ADMIN_REAL_NAME=${ADMIN_REAL_NAME:-系统管理员}
    
    # 生成 JWT 密钥
    JWT_SECRET=$(openssl rand -hex 32 2>/dev/null || cat /dev/urandom | tr -dc 'a-zA-Z0-9' | head -c 64)
    
    # 写入 .env 文件
    cat > "$ENV_FILE" << EOF
# MySQL Configuration
MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD
MYSQL_DATABASE=warehouse_db
MYSQL_USER=$MYSQL_USER
MYSQL_PASSWORD=$MYSQL_PASSWORD
MYSQL_PORT=3307

# Backend Configuration
DB_HOST=mysql
DB_PORT=3306
DB_NAME=warehouse_db
DB_USER=$MYSQL_USER
DB_PASSWORD=$MYSQL_PASSWORD
JWT_SECRET=$JWT_SECRET
JWT_ALGORITHM=HS256
JWT_EXPIRE_HOURS=24
ADMIN_USERNAME=$ADMIN_USERNAME
ADMIN_PASSWORD=$ADMIN_PASSWORD
ADMIN_REAL_NAME=$ADMIN_REAL_NAME

# Frontend Configuration
FRONTEND_PORT=3003
BACKEND_PORT=8003
NGINX_PORT=80

# Data Path
DATA_PATH=$DATA_PATH
EOF
    
    echo ""
    print_success ".env 文件已生成"
    echo ""
}

# 显示配置摘要
show_summary() {
    print_info "配置摘要"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    # 读取 .env 文件
    source .env
    
    echo "📁 数据存放路径: $DATA_PATH"
    echo ""
    echo "🗄️  数据库配置:"
    echo "   - ROOT 密码: ********"
    echo "   - 普通用户: $MYSQL_USER"
    echo "   - 普通密码: ********"
    echo "   - 端口: $MYSQL_PORT"
    echo ""
    echo "👤 管理员账号:"
    echo "   - 用户名: $ADMIN_USERNAME"
    echo "   - 密码: ********"
    echo "   - 昵称: $ADMIN_REAL_NAME"
    echo ""
    echo "🌐 服务端口:"
    echo "   - 前端: http://localhost:$FRONTEND_PORT"
    echo "   - 后端: http://localhost:$BACKEND_PORT"
    echo "   - MySQL: localhost:$MYSQL_PORT"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
}

# 启动服务
start_services() {
    print_info "正在启动服务..."
    echo ""
    
    # 创建必要的目录
    mkdir -p logs
    mkdir -p "$DATA_PATH/mysql"
    
    # 拉取镜像并启动
    docker-compose pull
    docker-compose up -d --build
    
    echo ""
    print_success "服务启动成功！"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "🎉 仓储物资出入库动态管理系统已启动"
    echo ""
    echo "📱 访问地址:"
    source .env
    echo "   - 前端界面: http://localhost:$FRONTEND_PORT"
    echo "   - API 文档: http://localhost:$BACKEND_PORT/docs"
    echo "   - 默认账号: $ADMIN_USERNAME / $ADMIN_PASSWORD"
    echo ""
    echo "⚙️  常用命令:"
    echo "   - 查看日志: docker-compose logs -f"
    echo "   - 停止服务: docker-compose down"
    echo "   - 重启服务: docker-compose restart"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# 主函数
main() {
    echo ""
    echo "╔═══════════════════════════════════════════════════════════╗"
    echo "║                                                           ║"
    echo "║     仓储物资出入库动态管理系统 - 启动脚本                  ║"
    echo "║                                                           ║"
    echo "╚═══════════════════════════════════════════════════════════╝"
    echo ""
    
    # 检查 Docker
    check_docker
    
    # 选择数据路径
    select_data_path
    
    # 设置环境变量
    setup_env
    
    # 显示配置摘要
    show_summary
    
    # 确认启动
    read -p "确认启动服务？(Y/n): " confirm
    if [[ "$confirm" =~ ^[Nn]$ ]]; then
        print_warning "已取消启动"
        exit 0
    fi
    
    # 启动服务
    start_services
}

# 运行主函数
main
