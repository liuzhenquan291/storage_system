@echo off
chcp 65001 >nul
title 仓储物资出入库动态管理系统 - 启动脚本

:: 仓储物资出入库动态管理系统 - Windows 启动脚本
:: 支持交互式配置和自动部署

setlocal enabledelayedexpansion

call :print_banner

:: 检查 Docker
call :check_docker
if errorlevel 1 exit /b 1

:: 选择数据路径
call :select_data_path

:: 设置环境变量
call :setup_env

:: 显示配置摘要
call :show_summary

:: 确认启动
echo.
set /p confirm="确认启动服务？(Y/n): "
if /i "!confirm!"=="n" (
    call :print_warning "已取消启动"
    pause
    exit /b 0
)

:: 启动服务
call :start_services

pause
exit /b 0

:: ============================================
:: 子程序
:: ============================================

:print_banner
cls
echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║                                                           ║
echo ║     仓储物资出入库动态管理系统 - 启动脚本                  ║
echo ║                                                           ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.
goto :eof

:print_info
echo [INFO] %~1
goto :eof

:print_success
echo [SUCCESS] %~1
goto :eof

:print_error
echo [ERROR] %~1
goto :eof

:print_warning
echo [WARNING] %~1
goto :eof

:check_docker
call :print_info "检查 Docker 安装状态..."

:: 检查 docker 命令
docker --version >nul 2>&1
if errorlevel 1 (
    call :print_error "Docker 未安装！"
    echo.
    echo 请按以下步骤安装 Docker：
    echo 1. 访问 https://docs.docker.com/desktop/install/windows-install/
    echo 2. 下载并安装 Docker Desktop
    echo 3. 启动 Docker Desktop 并等待其完全启动
    echo 4. 重新运行此脚本
    echo.
    echo 按任意键退出...
    pause >nul
    exit /b 1
)

:: 检查 Docker Compose
docker-compose --version >nul 2>&1
if errorlevel 1 (
    docker compose version >nul 2>&1
    if errorlevel 1 (
        call :print_error "Docker Compose 未安装！"
        echo Docker Desktop 已包含 Docker Compose。
        echo 请确保 Docker Desktop 已正确安装。
        pause
        exit /b 1
    )
)

:: 检查 Docker 是否正在运行
docker info >nul 2>&1
if errorlevel 1 (
    call :print_error "Docker 未运行！"
    echo 请启动 Docker Desktop 并等待其完全启动后再运行此脚本。
    pause
    exit /b 1
)

call :print_success "Docker 和 Docker Compose 已安装且运行正常"
echo.
goto :eof

:select_data_path
call :print_info "选择数据存放路径"
echo.
echo 请选择数据存放位置（包含数据库数据、日志等）：
echo.

:: 设置默认路径
set "DEFAULT_PATH=%USERPROFILE%\warehouse_data"
echo 默认路径: %DEFAULT_PATH%
echo.

set /p use_default="使用默认路径？(Y/n): "
if /i "!use_default!"=="n" (
    set /p DATA_PATH="请输入新的数据存放路径: "
    :: 去除引号
    set DATA_PATH=!DATA_PATH:"=!
) else (
    set "DATA_PATH=%DEFAULT_PATH%"
)

:: 创建目录
if not exist "!DATA_PATH!" mkdir "!DATA_PATH!"

call :print_success "数据将存放在: !DATA_PATH!"
echo.
goto :eof

:setup_env
call :print_info "配置系统参数"
echo.

set "ENV_FILE=.env"

:: 如果 .env 已存在，询问是否覆盖
if exist "%ENV_FILE%" (
    set /p reconfig=".env 文件已存在，是否重新配置？(y/N): "
    if /i not "!reconfig!"=="y" (
        call :print_info "使用现有的 .env 配置"
        goto :eof
    )
)

echo === 数据库配置 ===
echo.

:: MySQL ROOT 密码
set /p MYSQL_ROOT_PASSWORD="设置 MySQL ROOT 密码 (默认: root123): "
if "!MYSQL_ROOT_PASSWORD!"=="" set MYSQL_ROOT_PASSWORD=root123

:: 普通用户配置
set /p MYSQL_USER="设置数据库普通用户名 (默认: warehouse): "
if "!MYSQL_USER!"=="" set MYSQL_USER=warehouse

set /p MYSQL_PASSWORD="设置数据库普通用户密码 (默认: warehouse123): "
if "!MYSQL_PASSWORD!"=="" set MYSQL_PASSWORD=warehouse123

echo.
echo === 管理员账号配置 ===
echo.

set /p ADMIN_USERNAME="设置管理员用户名 (默认: admin): "
if "!ADMIN_USERNAME!"=="" set ADMIN_USERNAME=admin

set /p ADMIN_PASSWORD="设置管理员密码 (默认: admin123): "
if "!ADMIN_PASSWORD!"=="" set ADMIN_PASSWORD=admin123

set /p ADMIN_REAL_NAME="设置管理员昵称 (默认: 系统管理员): "
if "!ADMIN_REAL_NAME!"=="" set ADMIN_REAL_NAME=系统管理员

:: 生成 JWT 密钥
set JWT_SECRET=
for /f "tokens=*" %%a in ('powershell -Command "-join ((1..64) | ForEach-Object { Get-Random -Maximum 16 | ForEach-Object { '0123456789abcdef'[$_] })"') do set JWT_SECRET=%%a

:: 端口配置
set MYSQL_PORT=3307
set FRONTEND_PORT=3003
set BACKEND_PORT=8003
set NGINX_PORT=80

:: 写入 .env 文件
echo # MySQL Configuration>%ENV_FILE%
echo MYSQL_ROOT_PASSWORD=!MYSQL_ROOT_PASSWORD!>>%ENV_FILE%
echo MYSQL_DATABASE=warehouse_db>>%ENV_FILE%
echo MYSQL_USER=!MYSQL_USER!>>%ENV_FILE%
echo MYSQL_PASSWORD=!MYSQL_PASSWORD!>>%ENV_FILE%
echo MYSQL_PORT=!MYSQL_PORT!>>%ENV_FILE%
echo.>>%ENV_FILE%
echo # Backend Configuration>>%ENV_FILE%
echo DB_HOST=mysql>>%ENV_FILE%
echo DB_PORT=3306>>%ENV_FILE%
echo DB_NAME=warehouse_db>>%ENV_FILE%
echo DB_USER=!MYSQL_USER!>>%ENV_FILE%
echo DB_PASSWORD=!MYSQL_PASSWORD!>>%ENV_FILE%
echo JWT_SECRET=!JWT_SECRET!>>%ENV_FILE%
echo JWT_ALGORITHM=HS256>>%ENV_FILE%
echo JWT_EXPIRE_HOURS=24>>%ENV_FILE%
echo ADMIN_USERNAME=!ADMIN_USERNAME!>>%ENV_FILE%
echo ADMIN_PASSWORD=!ADMIN_PASSWORD!>>%ENV_FILE%
echo ADMIN_REAL_NAME=!ADMIN_REAL_NAME!>>%ENV_FILE%
echo.>>%ENV_FILE%
echo # Frontend Configuration>>%ENV_FILE%
echo FRONTEND_PORT=!FRONTEND_PORT!>>%ENV_FILE%
echo BACKEND_PORT=!BACKEND_PORT!>>%ENV_FILE%
echo NGINX_PORT=!NGINX_PORT!>>%ENV_FILE%
echo.>>%ENV_FILE%
echo # Data Path>>%ENV_FILE%
echo DATA_PATH=!DATA_PATH!>>%ENV_FILE%

echo.
call :print_success ".env 文件已生成"
echo.
goto :eof

:show_summary
call :print_info "配置摘要"
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

:: 读取 .env 文件
for /f "tokens=1,2 delims==" %%a in (.env) do (
    if "%%a"=="DATA_PATH" set DATA_PATH=%%b
    if "%%a"=="MYSQL_USER" set MYSQL_USER=%%b
    if "%%a"=="MYSQL_PORT" set MYSQL_PORT=%%b
    if "%%a"=="ADMIN_USERNAME" set ADMIN_USERNAME=%%b
    if "%%a"=="ADMIN_REAL_NAME" set ADMIN_REAL_NAME=%%b
    if "%%a"=="FRONTEND_PORT" set FRONTEND_PORT=%%b
    if "%%a"=="BACKEND_PORT" set BACKEND_PORT=%%b
)

echo 📁 数据存放路径: !DATA_PATH!
echo.
echo 🗄️  数据库配置:
echo    - 普通用户: !MYSQL_USER!
echo    - 端口: !MYSQL_PORT!
echo.
echo 👤 管理员账号:
echo    - 用户名: !ADMIN_USERNAME!
echo    - 昵称: !ADMIN_REAL_NAME!
echo.
echo 🌐 服务端口:
echo    - 前端: http://localhost:!FRONTEND_PORT!
echo    - 后端: http://localhost:!BACKEND_PORT!
echo    - MySQL: localhost:!MYSQL_PORT!
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
goto :eof

:start_services
call :print_info "正在启动服务..."
echo.

:: 创建必要的目录
if not exist logs mkdir logs
if not exist "!DATA_PATH!\mysql" mkdir "!DATA_PATH!\mysql"

:: 拉取镜像并启动
docker-compose pull
docker-compose up -d --build

if errorlevel 1 (
    call :print_error "服务启动失败！"
    echo 请检查 Docker 日志: docker-compose logs
    pause
    exit /b 1
)

echo.
call :print_success "服务启动成功！"
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo 🎉 仓储物资出入库动态管理系统已启动
echo.

:: 重新读取端口
for /f "tokens=1,2 delims==" %%a in (.env) do (
    if "%%a"=="FRONTEND_PORT" set FRONTEND_PORT=%%b
    if "%%a"=="BACKEND_PORT" set BACKEND_PORT=%%b
    if "%%a"=="ADMIN_USERNAME" set ADMIN_USERNAME=%%b
    if "%%a"=="ADMIN_PASSWORD" set ADMIN_PASSWORD=%%b
)

echo 📱 访问地址:
echo    - 前端界面: http://localhost:!FRONTEND_PORT!
echo    - API 文档: http://localhost:!BACKEND_PORT!/docs
echo    - 默认账号: !ADMIN_USERNAME! / !ADMIN_PASSWORD!
echo.
echo ⚙️  常用命令:
echo    - 查看日志: docker-compose logs -f
echo    - 停止服务: docker-compose down
echo    - 重启服务: docker-compose restart
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
goto :eof
