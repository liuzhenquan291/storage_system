"""
Windows 7 适配配置 - 使用 SQLite 代替 MySQL
"""
import os
import sys
from pathlib import Path

# 检测运行环境
IS_BUNDLE = getattr(sys, 'frozen', False)
BASE_DIR = Path(sys.executable).parent if IS_BUNDLE else Path(__file__).parent.parent.parent

# 数据库配置
if IS_BUNDLE or os.getenv('USE_SQLITE', 'false').lower() == 'true':
    # Win7 打包环境使用 SQLite
    DATA_DIR = BASE_DIR / 'data'
    DATA_DIR.mkdir(exist_ok=True)
    DATABASE_URL = f"sqlite:///{DATA_DIR}/warehouse.db"
    DB_ECHO = False
else:
    # 开发环境使用 MySQL
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "mysql+aiomysql://warehouse:warehouse123@localhost:3307/warehouse_db"
    )
    DB_ECHO = os.getenv("DB_ECHO", "false").lower() == "true"

# JWT 配置
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_HOURS = int(os.getenv("JWT_EXPIRE_HOURS", "24"))

# 管理员配置
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
ADMIN_REAL_NAME = os.getenv("ADMIN_REAL_NAME", "系统管理员")

# 端口配置
BACKEND_PORT = int(os.getenv("BACKEND_PORT", "8003"))
FRONTEND_PORT = int(os.getenv("FRONTEND_PORT", "3003"))

# 静态文件目录（打包后）
STATIC_DIR = BASE_DIR / 'static' if IS_BUNDLE else None
