"""
配置管理
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置"""
    
    # Database
    DB_TYPE: str = "mysql"  # mysql 或 sqlite
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_NAME: str = "warehouse_db"
    DB_USER: str = "warehouse"
    DB_PASSWORD: str = "warehouse123"
    SQLITE_PATH: str = "./warehouse.db"  # SQLite 数据库路径
    
    # JWT
    JWT_SECRET: str = "your-super-secret-jwt-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_HOURS: int = 2
    
    # Admin
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin123"
    ADMIN_REAL_NAME: str = "系统管理员"
    
    @property
    def DATABASE_URL(self) -> str:
        """数据库连接URL"""
        if self.DB_TYPE.lower() == "sqlite":
            return f"sqlite+aiosqlite:///{self.SQLITE_PATH}"
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
