"""
数据库连接配置
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# 判断数据库类型
is_sqlite = settings.DB_TYPE.lower() == "sqlite"

# 同步引擎（用于初始化）
if is_sqlite:
    sync_database_url = settings.DATABASE_URL.replace("+aiosqlite", "")
    sync_engine = create_engine(
        sync_database_url,
        echo=False,
        connect_args={"check_same_thread": False}
    )
else:
    sync_database_url = settings.DATABASE_URL.replace("+pymysql", "+aiomysql")
    sync_engine = create_engine(
        sync_database_url,
        echo=False,
        pool_pre_ping=True,
        pool_recycle=3600
    )

# 异步引擎
if is_sqlite:
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False}
    )
else:
    async_database_url = settings.DATABASE_URL.replace("+pymysql", "+aiomysql")
    engine = create_async_engine(
        async_database_url,
        echo=False,
        pool_pre_ping=True,
        pool_recycle=3600
    )

# 异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

# 基础模型类
Base = declarative_base()


async def get_db():
    """获取数据库会话"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
