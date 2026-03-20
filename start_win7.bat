@echo off
chcp 65001 >nul
title 仓储物资出入库动态管理系统 - Win7 启动脚本

:: Windows 7 兼容启动脚本
:: 不依赖 Docker，直接使用 Python + Node.js

setlocal enabledelayedexpansion

call :print_banner

:: 检查必要软件
call :check_requirements
if errorlevel 1 exit /b 1

:: 配置环境
call :setup_config

:: 初始化数据库
call :init_database

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
echo ║     仓储物资出入库动态管理系统 - Win7 版本                ║
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

:check_requirements
call :print_info "检查系统环境..."
echo.

:: 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    call :print_error "Python 未安装！"
    echo.
    echo 请安装 Python 3.8 或更高版本：
    echo https://www.python.org/downloads/release/python-3810/
    echo.
    echo 安装时请务必勾选 "Add Python to PATH"
    pause
    exit /b 1
)
for /f "tokens=*" %%a in ('python --version 2^>^&1') do set PYTHON_VER=%%a
echo   ✓ Python: %PYTHON_VER%

:: 检查 pip
pip --version >nul 2>&1
if errorlevel 1 (
    call :print_error "pip 未安装！"
    pause
    exit /b 1
)
echo   ✓ pip: 已安装

:: 检查 Node.js
node --version >nul 2>&1
if errorlevel 1 (
    call :print_error "Node.js 未安装！"
    echo.
    echo 请安装 Node.js 16.x LTS 版本：
    echo https://nodejs.org/dist/v16.20.2/node-v16.20.2-x86.msi
    pause
    exit /b 1
)
for /f "tokens=*" %%a in ('node --version') do set NODE_VER=%%a
echo   ✓ Node.js: %NODE_VER%

:: 检查 npm
npm --version >nul 2>&1
if errorlevel 1 (
    call :print_error "npm 未安装！"
    pause
    exit /b 1
)
echo   ✓ npm: 已安装

:: 检查 MySQL（使用嵌入式或检查是否已安装）
if exist "mysql\bin\mysqld.exe" (
    echo   ✓ MySQL: 便携版已存在
) else (
    echo   ⚠ MySQL: 将使用 SQLite 替代（无需安装）
)

call :print_success "环境检查通过"
echo.
goto :eof

:setup_config
call :print_info "配置系统参数"
echo.

set "ENV_FILE=.env.win7"

:: 如果配置文件已存在，询问是否覆盖
if exist "%ENV_FILE%" (
    set /p reconfig=".env.win7 已存在，是否重新配置？(y/N): "
    if /i not "!reconfig!"=="y" (
        call :print_info "使用现有配置"
        goto :eof
    )
)

echo === 系统配置 ===
echo.

:: 数据路径
set /p DATA_PATH="数据存放路径 (默认: %CD%\data): "
if "!DATA_PATH!"=="" set "DATA_PATH=%CD%\data"

:: 管理员配置
set /p ADMIN_USERNAME="管理员用户名 (默认: admin): "
if "!ADMIN_USERNAME!"=="" set ADMIN_USERNAME=admin

set /p ADMIN_PASSWORD="管理员密码 (默认: admin123): "
if "!ADMIN_PASSWORD!"=="" set ADMIN_PASSWORD=admin123

:: 端口配置
echo.
echo === 端口配置 (保持默认即可) ===
set /p BACKEND_PORT="后端端口 (默认: 8003): "
if "!BACKEND_PORT!"=="" set BACKEND_PORT=8003

set /p FRONTEND_PORT="前端端口 (默认: 3003): "
if "!FRONTEND_PORT!"=="" set FRONTEND_PORT=3003

:: 生成密钥
for /f "tokens=*" %%a in ('powershell -Command "-join ((1..32) | ForEach-Object { Get-Random -Maximum 16 | ForEach-Object { '0123456789abcdef'[$_] })"') do set JWT_SECRET=%%a

:: 写入配置文件
echo # Win7 环境配置 > %ENV_FILE%
echo DATA_PATH=!DATA_PATH! >> %ENV_FILE%
echo ADMIN_USERNAME=!ADMIN_USERNAME! >> %ENV_FILE%
echo ADMIN_PASSWORD=!ADMIN_PASSWORD! >> %ENV_FILE%
echo BACKEND_PORT=!BACKEND_PORT! >> %ENV_FILE%
echo FRONTEND_PORT=!FRONTEND_PORT! >> %ENV_FILE%
echo JWT_SECRET=!JWT_SECRET! >> %ENV_FILE%
echo DATABASE_URL=sqlite:///!DATA_PATH!\warehouse.db >> %ENV_FILE%

:: 创建目录
if not exist "!DATA_PATH!" mkdir "!DATA_PATH!"
if not exist "!DATA_PATH!\logs" mkdir "!DATA_PATH!\logs"

call :print_success "配置完成"
echo.
goto :eof

:init_database
call :print_info "初始化数据库..."
echo.

:: 检查是否已初始化
if exist "%DATA_PATH%\warehouse.db" (
    call :print_info "数据库已存在，跳过初始化"
    goto :eof
)

:: 安装 Python 依赖
call :print_info "安装后端依赖..."
cd backend
pip install -r requirements.txt -q
if errorlevel 1 (
    call :print_error "依赖安装失败"
    cd ..
    pause
    exit /b 1
)

:: 初始化数据库
call :print_info "创建数据库表..."
python -c "
import sys
sys.path.insert(0, '.')
from app.core.database import engine, Base
from app.models import *
import asyncio

async def init():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print('数据库初始化完成')

asyncio.run(init())
"

cd ..
call :print_success "数据库初始化完成"
echo.
goto :eof

:start_services
call :print_info "启动服务..."
echo.

:: 读取配置
for /f "tokens=1,2 delims==" %%a in (.env.win7) do (
    if "%%a"=="BACKEND_PORT" set BACKEND_PORT=%%b
    if "%%a"=="FRONTEND_PORT" set FRONTEND_PORT=%%b
    if "%%a"=="ADMIN_USERNAME" set ADMIN_USERNAME=%%b
    if "%%a"=="ADMIN_PASSWORD" set ADMIN_PASSWORD=%%b
)

:: 启动后端
call :print_info "启动后端服务..."
start "仓储系统-后端" cmd /k "cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port %BACKEND_PORT%"

:: 等待后端启动
timeout /t 3 /nobreak >nul

:: 启动前端
call :print_info "启动前端服务..."
start "仓储系统-前端" cmd /k "cd frontend && npm run dev -- --port %FRONTEND_PORT%"

:: 等待前端启动
timeout /t 5 /nobreak >nul

echo.
call :print_success "服务启动成功！"
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo 🎉 仓储物资出入库动态管理系统已启动
echo.
echo 📱 访问地址:
echo    - 前端界面: http://localhost:%FRONTEND_PORT%
echo    - API 文档: http://localhost:%BACKEND_PORT%/docs
echo    - 管理员账号: %ADMIN_USERNAME% / %ADMIN_PASSWORD%
echo.
echo ⚠️  注意：
echo    - 请勿关闭弹出的命令行窗口
echo    - 窗口最小化即可在后台运行
echo    - 关闭窗口将停止服务
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

:: 自动打开浏览器
start http://localhost:%FRONTEND_PORT%

goto :eof
