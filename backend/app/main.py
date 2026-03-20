"""
仓储物资出入库动态管理系统 - 后端入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import sys

from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1 import auth, user, role, menu, warehouse, material, order, device, dashboard, resource

# Configure logger
logger.remove()
logger.add(sys.stdout, level="INFO", format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}")
logger.add("logs/app.log", rotation="1 day", retention="7 days", level="INFO")

# Create FastAPI app
app = FastAPI(
    title="仓储物资出入库动态管理系统",
    description="仓储物资出入库动态管理系统后端API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["认证"])
app.include_router(user.router, prefix="/api/v1/users", tags=["用户管理"])
app.include_router(role.router, prefix="/api/v1/roles", tags=["角色管理"])
app.include_router(menu.router, prefix="/api/v1/menus", tags=["菜单管理"])
app.include_router(resource.router, prefix="/api/v1/resources", tags=["资源管理"])
app.include_router(warehouse.router, prefix="/api/v1/warehouse", tags=["库房管理"])
app.include_router(material.router, prefix="/api/v1/materials", tags=["物资管理"])
app.include_router(order.router, prefix="/api/v1/orders", tags=["工单管理"])
app.include_router(device.router, prefix="/api/v1/devices", tags=["设备管理"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["仪表盘"])


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("Starting application...")
    
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("Database tables created")
    
    # Initialize resources
    from app.services.auth_service import AuthService
    await AuthService.init_resources()
    logger.info("Resources initialized")
    
    # Initialize admin user
    await AuthService.init_admin()
    logger.info("Admin user initialized")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("Shutting down application...")


@app.get("/")
async def root():
    """根路径"""
    return {"message": "仓储物资出入库动态管理系统 API", "version": "1.0.0"}


@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
