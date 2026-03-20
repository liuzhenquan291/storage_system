#!/usr/bin/env python3
"""
Windows 7 系统打包脚本
将后端和前端打包为 standalone EXE
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_step(msg):
    print(f"\n{'='*60}")
    print(f"  {msg}")
    print('='*60)

def check_requirements():
    """检查打包环境"""
    print_step("检查打包环境")
    
    # 检查 Python
    try:
        result = subprocess.run(['python', '--version'], capture_output=True, text=True)
        print(f"✓ Python: {result.stdout.strip() or result.stderr.strip()}")
    except:
        print("✗ Python 未安装")
        return False
    
    # 检查 PyInstaller
    try:
        import PyInstaller
        print("✓ PyInstaller: 已安装")
    except:
        print("⚠ PyInstaller 未安装，正在安装...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'], check=True)
        print("✓ PyInstaller: 安装完成")
    
    # 检查 Node.js
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        print(f"✓ Node.js: {result.stdout.strip()}")
    except:
        print("✗ Node.js 未安装，请先安装 Node.js 16.x")
        return False
    
    return True

def build_frontend():
    """构建前端"""
    print_step("构建前端项目")
    
    frontend_dir = Path('frontend')
    if not frontend_dir.exists():
        print("✗ 找不到 frontend 目录")
        return False
    
    os.chdir(frontend_dir)
    
    # 安装依赖
    print("安装前端依赖...")
    result = subprocess.run(['npm', 'install'], capture_output=True)
    if result.returncode != 0:
        print("✗ npm install 失败")
        print(result.stderr.decode())
        os.chdir('..')
        return False
    
    # 构建生产版本
    print("构建生产版本...")
    result = subprocess.run(['npm', 'run', 'build'], capture_output=True)
    if result.returncode != 0:
        print("✗ 构建失败")
        print(result.stderr.decode())
        os.chdir('..')
        return False
    
    os.chdir('..')
    print("✓ 前端构建完成")
    return True

def modify_backend_for_sqlite():
    """修改后端使用 SQLite"""
    print_step("适配 SQLite 数据库")
    
    config_file = Path('backend/app/core/config.py')
    if not config_file.exists():
        print("✗ 找不到配置文件")
        return False
    
    # 备份原文件
    shutil.copy(config_file, config_file.with_suffix('.py.bak'))
    
    # 读取并修改
    content = config_file.read_text(encoding='utf-8')
    
    # 添加 SQLite 适配
    sqlite_adapter = '''
# Windows 7 打包适配
import sys
IS_BUNDLE = getattr(sys, 'frozen', False)
if IS_BUNDLE:
    # 使用 SQLite
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///warehouse.db")
'''
    
    if 'IS_BUNDLE' not in content:
        # 在文件开头添加适配代码
        lines = content.split('\n')
        import_idx = 0
        for i, line in enumerate(lines):
            if line.startswith('import') or line.startswith('from'):
                import_idx = i + 1
        lines.insert(import_idx, sqlite_adapter)
        config_file.write_text('\n'.join(lines), encoding='utf-8')
    
    print("✓ 已适配 SQLite")
    return True

def build_backend():
    """打包后端"""
    print_step("打包后端服务")
    
    # PyInstaller 参数
    args = [
        'backend/app/main.py',
        '--name=仓储系统-后端',
        '--onefile',
        # '--windowed',  # 调试用，完成后启用
        '--distpath=dist_win7',
        '--workpath=build_win7',
        '--specpath=build_win7',
        f'--add-data=backend/app;app',
        '--hidden-import=uvicorn.logging',
        '--hidden-import=uvicorn.loops.auto',
        '--hidden-import=uvicorn.protocols.http.auto',
        '--hidden-import=uvicorn.protocols.websockets.auto',
        '--hidden-import=uvicorn.lifespan.on',
        '--hidden-import=asyncio',
        '--hidden-import=sqlite3',
    ]
    
    # 添加前端静态文件
    frontend_dist = Path('frontend/dist')
    if frontend_dist.exists():
        args.append(f'--add-data=frontend/dist;static')
    
    try:
        import PyInstaller.__main__
        PyInstaller.__main__.run(args)
        print("✓ 后端打包完成")
        return True
    except Exception as e:
        print(f"✗ 打包失败: {e}")
        return False

def create_launcher():
    """创建启动器"""
    print_step("创建启动器")
    
    launcher_code = '''
import subprocess
import sys
import os
import time
import webbrowser
from pathlib import Path

def main():
    base_dir = Path(__file__).parent
    
    print("="*60)
    print("  仓储物资出入库动态管理系统")
    print("  Windows 7 兼容版本")
    print("="*60)
    print()
    
    # 启动后端
    backend_exe = base_dir / '仓储系统-后端.exe'
    if not backend_exe.exists():
        print("错误：找不到后端程序")
        input("按回车键退出...")
        return
    
    print("正在启动后端服务...")
    backend_proc = subprocess.Popen(
        [str(backend_exe)],
        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
    )
    
    # 等待后端启动
    time.sleep(5)
    
    # 打开浏览器
    print("正在打开浏览器...")
    webbrowser.open('http://localhost:8003')
    
    print()
    print("="*60)
    print("  系统已启动！")
    print("  访问地址: http://localhost:8003")
    print("  默认账号: admin / admin123")
    print()
    print("  请勿关闭此窗口")
    print("  关闭窗口将停止服务")
    print("="*60)
    
    input()
    
    # 停止服务
    print("\\n正在停止服务...")
    backend_proc.terminate()
    backend_proc.wait(timeout=5)
    print("✓ 服务已停止")

if __name__ == '__main__':
    main()
'''
    
    launcher_file = Path('launcher_win7.py')
    launcher_file.write_text(launcher_code, encoding='utf-8')
    
    # 打包启动器
    args = [
        'launcher_win7.py',
        '--name=启动仓储系统',
        '--onefile',
        '--windowed',
        '--icon=NONE',
        '--distpath=dist_win7',
        '--workpath=build_win7',
    ]
    
    try:
        import PyInstaller.__main__
        PyInstaller.__main__.run(args)
        print("✓ 启动器创建完成")
        return True
    except Exception as e:
        print(f"✗ 启动器创建失败: {e}")
        return False

def create_distribution():
    """创建发行包"""
    print_step("创建发行包")
    
    dist_dir = Path('dist_win7')
    if not dist_dir.exists():
        print("✗ 找不到打包输出目录")
        return False
    
    # 创建说明文件
    readme = '''仓储物资出入库动态管理系统 - Windows 7 版本

使用方法：
1. 解压本压缩包到任意目录
2. 双击运行 "启动仓储系统.exe"
3. 等待系统自动打开浏览器
4. 使用默认账号登录：admin / admin123

注意事项：
- 首次启动需要初始化数据库，请耐心等待
- 请勿关闭弹出的命令行窗口
- 数据存储在程序目录下的 warehouse.db 文件中
- 建议定期备份 warehouse.db 文件

技术支持：
如有问题请联系开发团队
'''
    (dist_dir / '使用说明.txt').write_text(readme, encoding='utf-8')
    
    # 创建 ZIP 压缩包
    print("创建 ZIP 压缩包...")
    shutil.make_archive('仓储系统_Win7_完整版', 'zip', 'dist_win7')
    
    print("✓ 发行包已创建: 仓储系统_Win7_完整版.zip")
    return True

def main():
    """主函数"""
    print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║     仓储物资出入库动态管理系统 - Win7 打包工具            ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """)
    
    # 检查环境
    if not check_requirements():
        print("\n✗ 环境检查失败，请安装必要的软件")
        input("按回车键退出...")
        return
    
    # 构建前端
    if not build_frontend():
        print("\n✗ 前端构建失败")
        input("按回车键退出...")
        return
    
    # 适配后端
    if not modify_backend_for_sqlite():
        print("\n⚠ 后端适配警告（可能不影响运行）")
    
    # 打包后端
    if not build_backend():
        print("\n✗ 后端打包失败")
        input("按回车键退出...")
        return
    
    # 创建启动器
    if not create_launcher():
        print("\n⚠ 启动器创建失败")
    
    # 创建发行包
    if not create_distribution():
        print("\n⚠ 发行包创建失败")
    
    print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║     打包完成！                                            ║
║                                                           ║
║     输出文件: 仓储系统_Win7_完整版.zip                    ║
║                                                           ║
║     使用方法:                                             ║
║     1. 将 ZIP 文件复制到 Win7 电脑                        ║
║     2. 解压到任意目录                                     ║
║     3. 双击 "启动仓储系统.exe"                            ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """)
    
    input("按回车键退出...")

if __name__ == '__main__':
    main()
