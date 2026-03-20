"""
认证服务
"""
from typing import Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.models.sys_user import SysUser
from app.models.sys_role import SysRole, SysRoleMenu
from app.models.sys_resource import SysResource, SysRoleResource
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.config import settings
from app.core.permissions import PERMISSIONS, SUPER_ADMIN_PERMISSIONS
from app.schemas.user import UserLogin, UserCreate, UserResponse, TokenResponse
from loguru import logger


class AuthService:
    """认证服务"""
    
    @staticmethod
    async def login(db: AsyncSession, login_data: UserLogin) -> Optional[TokenResponse]:
        """用户登录"""
        # 查询用户
        result = await db.execute(
            select(SysUser).where(
                SysUser.username == login_data.username,
                SysUser.deleted == 0
            )
        )
        user = result.scalar_one_or_none()
        
        if not user:
            return None
        
        # 验证密码
        if not verify_password(login_data.password, user.password):
            return None
        
        # 检查状态
        if user.status != 1:
            return None
        
        # 生成token
        access_token = create_access_token(
            data={"sub": user.username, "user_id": user.id}
        )
        
        return TokenResponse(
            access_token=access_token,
            user=UserResponse(**user.to_dict())
        )
    
    @staticmethod
    async def init_resources() -> bool:
        """初始化资源数据"""
        from app.core.database import AsyncSessionLocal
        
        async with AsyncSessionLocal() as db:
            try:
                for perm in PERMISSIONS:
                    # 检查是否已存在
                    result = await db.execute(
                        select(SysResource).where(SysResource.code == perm["code"])
                    )
                    if result.scalar_one_or_none():
                        continue
                    
                    resource = SysResource(
                        code=perm["code"],
                        name=perm["name"],
                        description=perm.get("description", "")
                    )
                    db.add(resource)
                
                await db.commit()
                logger.info("Resources initialized")
                return True
                
            except Exception as e:
                logger.error(f"Failed to init resources: {e}")
                await db.rollback()
                return False
    
    @staticmethod
    async def init_admin() -> bool:
        """初始化管理员账号和权限"""
        from app.core.database import AsyncSessionLocal
        
        async with AsyncSessionLocal() as db:
            try:
                # 检查是否已存在管理员
                result = await db.execute(
                    select(SysUser).where(SysUser.username == settings.ADMIN_USERNAME)
                )
                admin = result.scalar_one_or_none()
                
                if admin:
                    logger.info("Admin user already exists")
                    return False
                
                # 创建或获取超级管理员角色
                result = await db.execute(
                    select(SysRole).where(SysRole.role_code == "super_admin")
                )
                role = result.scalar_one_or_none()
                
                if not role:
                    role = SysRole(
                        role_name="超级管理员",
                        role_code="super_admin",
                        description="系统超级管理员，拥有所有权限"
                    )
                    db.add(role)
                    await db.flush()
                
                # 创建管理员用户
                admin = SysUser(
                    username=settings.ADMIN_USERNAME,
                    password=get_password_hash(settings.ADMIN_PASSWORD),
                    real_name=settings.ADMIN_REAL_NAME,
                    role_id=role.id,
                    status=1,
                    deleted=0
                )
                db.add(admin)
                
                # 为超级管理员角色分配所有资源权限
                result = await db.execute(select(SysResource))
                resources = result.scalars().all()
                
                for resource in resources:
                    # 检查是否已存在
                    result = await db.execute(
                        select(SysRoleResource).where(
                            SysRoleResource.role_id == role.id,
                            SysRoleResource.resource_id == resource.id
                        )
                    )
                    if result.scalar_one_or_none():
                        continue
                    
                    role_resource = SysRoleResource(
                        role_id=role.id,
                        resource_id=resource.id
                    )
                    db.add(role_resource)
                
                await db.commit()
                
                logger.info(f"Admin user created: {settings.ADMIN_USERNAME}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to init admin: {e}")
                await db.rollback()
                return False
    
    @staticmethod
    async def get_current_user(db: AsyncSession, user_id: int) -> Optional[SysUser]:
        """获取当前用户"""
        result = await db.execute(
            select(SysUser).where(
                SysUser.id == user_id,
                SysUser.deleted == 0
            )
        )
        return result.scalar_one_or_none()
