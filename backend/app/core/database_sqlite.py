"""
SQLite 数据库连接配置 - 用于 Windows 7 部署
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
import os

# 判断使用哪种数据库
DATABASE_URL = os.getenv("DATABASE_URL", "")
USE_SQLITE = DATABASE_URL.startswith("sqlite")

Base = declarative_base()

if USE_SQLITE:
    # SQLite 同步模式
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False}
    )
    
    SessionLocal = sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False
    )
    
    # 为了兼容异步接口，创建一个同步包装器
    class AsyncSessionWrapper:
        """将同步 Session 包装为异步接口"""
        def __init__(self, session):
            self._session = session
        
        async def execute(self, *args, **kwargs):
            return self._session.execute(*args, **kwargs)
        
        async def commit(self):
            self._session.commit()
        
        async def rollback(self):
            self._session.rollback()
        
        async def close(self):
            self._session.close()
        
        async def flush(self):
            self._session.flush()
        
        def add(self, obj):
            self._session.add(obj)
        
        def add_all(self, objs):
            self._session.add_all(objs)
        
        async def delete(self, obj):
            self._session.delete(obj)
        
        async def refresh(self, obj):
            self._session.refresh(obj)
        
        async def run_sync(self, func, *args, **kwargs):
            """运行同步函数"""
            return func(self._session, *args, **kwargs)
    
    class AsyncSessionLocalWrapper:
        """异步会话工厂包装器"""
        def __init__(self):
            pass
        
        def __call__(self):
            session = SessionLocal()
            return AsyncSessionWrapper(session)
        
        async def __aenter__(self):
            return self()
        
        async def __aexit__(self, *args):
            pass
    
    AsyncSessionLocal = AsyncSessionLocalWrapper()
    
    async def get_db():
        """获取数据库会话"""
        session = SessionLocal()
        wrapper = AsyncSessionWrapper(session)
        try:
            yield wrapper
            await wrapper.commit()
        except Exception:
            await wrapper.rollback()
            raise
        finally:
            await wrapper.close()

else:
    # MySQL 异步模式（原有代码）
    from sqlalchemy.ext.asyncio import create_async_engine
    
    engine = create_async_engine(
        DATABASE_URL.replace("+pymysql", "+aiomysql"),
        echo=False,
        pool_pre_ping=True,
        pool_recycle=3600
    )
    
    AsyncSessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False
    )
    
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
