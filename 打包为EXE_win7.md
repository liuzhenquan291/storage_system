# Windows 7 系统打包为 EXE 方案

## 方案概述

将仓储系统打包为 ** standalone EXE 应用程序**，客户无需安装 Python、Node.js，双击即可运行。

## 方案对比

| 方案 | 优点 | 缺点 | 推荐度 |
|------|------|------|--------|
| **方案A：PyInstaller + PyWebView** | 单文件、体积小 | 界面简单 | ⭐⭐⭐⭐⭐ |
| **方案B：PyInstaller + 内嵌浏览器** | 功能完整、独立运行 | 体积大(约500MB) | ⭐⭐⭐⭐ |
| **方案C：Electron + Python 后端** | 界面美观 | 打包复杂 | ⭐⭐⭐ |

## 推荐方案A：PyInstaller 单文件打包（最简单）

### 步骤1：安装打包工具

```cmd
# 在开发电脑上安装
pip install pyinstaller
pip install pywebview
```

### 步骤2：创建打包脚本

创建文件 `build_win7_exe.py`：

```python
#!/usr/bin/env python3
"""
Windows 7 系统打包脚本
生成 standalone EXE 文件
"""

import PyInstaller.__main__
import os
import shutil

# 清理旧构建
if os.path.exists('dist'):
    shutil.rmtree('dist')
if os.path.exists('build'):
    shutil.rmtree('build')

# PyInstaller 配置
PyInstaller.__main__.run([
    'backend/app/main.py',           # 入口文件
    '--name=仓储管理系统',            # 应用名称
    '--onefile',                      # 单文件
    '--windowed',                     # 无控制台窗口
    '--icon=assets/icon.ico',         # 图标
    '--add-data=backend/app;app',     # 包含后端代码
    '--add-data=frontend/dist;frontend',  # 包含前端构建文件
    '--hidden-import=uvicorn',
    '--hidden-import=fastapi',
    '--hidden-import=sqlalchemy',
    '--hidden-import=sqlite3',
    '--hidden-import=jose',
    '--hidden-import=passlib',
    '--hidden-import=bcrypt',
    '--collect-all=fastapi',
    '--collect-all=uvicorn',
])

print("✅ 打包完成！")
print("输出文件: dist/仓储管理系统.exe")
```

### 步骤3：修改后端适配 SQLite

修改 `backend/app/core/config.py`：

```python
import os

class Settings:
    # 检测是否为打包环境
    IS_BUNDLE = getattr(sys, 'frozen', False)
    
    # 数据库配置 - Win7 使用 SQLite
    if IS_BUNDLE:
        # 打包后使用 SQLite
        DATABASE_URL = f"sqlite:///{os.path.expanduser('~/warehouse.db')}"
    else:
        # 开发环境使用 MySQL
        DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://...")
```

### 步骤4：修改前端 API 地址

修改 `frontend/.env.production`：

```
VITE_API_BASE_URL=http://localhost:8003/api/v1
```

### 步骤5：执行打包

```cmd
# 1. 构建前端
cd frontend
npm run build
cd ..

# 2. 运行打包脚本
python build_win7_exe.py

# 3. 输出在 dist/仓储管理系统.exe
```

## 推荐方案B：双进程打包（功能完整）

### 目录结构

```
仓储系统_Win7/
├── start.exe              # 启动器（Python 打包）
├── backend.exe            # 后端服务
├── frontend.exe           # 前端服务
├── data/                  # 数据目录
└── config.ini            # 配置文件
```

### 启动器代码

创建 `launcher.py`：

```python
"""
Windows 7 系统启动器
管理后端和前端进程
"""

import subprocess
import sys
import os
import webbrowser
from pathlib import Path
import configparser

class WarehouseLauncher:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.config = self.load_config()
        self.processes = []
        
    def load_config(self):
        """加载配置"""
        config = configparser.ConfigParser()
        config_file = self.base_dir / 'config.ini'
        
        if not config_file.exists():
            # 创建默认配置
            config['DEFAULT'] = {
                'backend_port': '8003',
                'frontend_port': '3003',
                'admin_username': 'admin',
                'admin_password': 'admin123'
            }
            with open(config_file, 'w') as f:
                config.write(f)
        else:
            config.read(config_file)
            
        return config
    
    def start_backend(self):
        """启动后端"""
        backend_exe = self.base_dir / 'backend.exe'
        if not backend_exe.exists():
            print("错误：找不到后端程序 backend.exe")
            return False
            
        process = subprocess.Popen(
            [str(backend_exe)],
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        self.processes.append(process)
        print(f"✓ 后端服务已启动 (PID: {process.pid})")
        return True
    
    def start_frontend(self):
        """启动前端"""
        frontend_exe = self.base_dir / 'frontend.exe'
        if not frontend_exe.exists():
            print("错误：找不到前端程序 frontend.exe")
            return False
            
        process = subprocess.Popen(
            [str(frontend_exe)],
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        self.processes.append(process)
        print(f"✓ 前端服务已启动 (PID: {process.pid})")
        return True
    
    def open_browser(self):
        """打开浏览器"""
        port = self.config.get('DEFAULT', 'frontend_port', fallback='3003')
        url = f"http://localhost:{port}"
        webbrowser.open(url)
        print(f"✓ 已打开浏览器: {url}")
    
    def run(self):
        """运行启动器"""
        print("=" * 50)
        print("仓储物资出入库动态管理系统")
        print("Windows 7 兼容版本")
        print("=" * 50)
        print()
        
        # 启动服务
        if not self.start_backend():
            input("按回车键退出...")
            return
            
        import time
        time.sleep(3)  # 等待后端启动
        
        if not self.start_frontend():
            input("按回车键退出...")
            return
            
        time.sleep(2)
        
        # 打开浏览器
        self.open_browser()
        
        print()
        print("=" * 50)
        print("系统已启动！请勿关闭此窗口。")
        print("关闭此窗口将停止所有服务。")
        print("=" * 50)
        
        # 等待用户按回车
        input()
        
        # 清理进程
        self.cleanup()
    
    def cleanup(self):
        """清理进程"""
        print("\n正在停止服务...")
        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                process.kill()
        print("✓ 所有服务已停止")

if __name__ == '__main__':
    launcher = WarehouseLauncher()
    try:
        launcher.run()
    except KeyboardInterrupt:
        launcher.cleanup()
```

### 打包命令

```cmd
# 打包启动器
pyinstaller --onefile --windowed --name=start launcher.py

# 打包后端
pyinstaller --onefile --windowed backend/app/main.py --name=backend

# 打包前端（使用 pkg）
cd frontend
pkg package.json -t node16-win-x64
```

## 客户部署步骤

### 方式1：单文件部署（最简单）

1. 复制 `仓储管理系统.exe` 到客户电脑
2. 双击运行
3. 系统自动打开浏览器
4. 默认账号：admin / admin123

### 方式2：文件夹部署（推荐）

1. 解压 `仓储系统_Win7.zip` 到任意目录
2. 双击 `start.exe`
3. 系统自动配置并启动
4. 打开浏览器访问 http://localhost:3003

## 常见问题

### Q: Win7 提示缺少 DLL？
A: 安装 Visual C++ Redistributable：
https://aka.ms/vs/17/release/vc_redist.x64.exe

### Q: 提示无法启动此程序？
A: 确保 Win7 已安装 SP1 补丁和 .NET Framework 4.5+

### Q: 如何修改数据库位置？
A: 修改 config.ini 中的 data_path 配置项

### Q: 如何备份数据？
A: 复制 data 文件夹即可，内含 SQLite 数据库文件

## 技术支持

如需协助打包，请提供：
1. 开发环境（Python版本、Node版本）
2. 是否需要修改 Logo
3. 默认管理员账号密码
