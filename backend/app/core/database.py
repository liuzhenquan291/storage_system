"""
数据库连接配置
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# 同步引擎（用于初始化）
sync_engine = create_engine(
    settings.DATABASE_URL.replace("+pymysql", "+aiomysql"),
    echo=False,
    pool_pre_ping=True,
    pool_recycle=3600
)

# 异步引擎
engine = create_async_engine(
    settings.DATABASE_URL.replace("+pymysql", "+aiomysql"),
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
