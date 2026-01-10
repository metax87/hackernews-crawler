"""
数据库连接配置

使用 SQLAlchemy 2.0 异步引擎。
支持 SQLite（开发）和 PostgreSQL（生产）。
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


# 创建异步引擎
engine = create_async_engine(
    settings.database_url,
    echo=settings.db_echo,  # 开发时可以设置为 True 查看 SQL
    future=True,
)

# 会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# 基类
class Base(DeclarativeBase):
    """所有模型的基类"""

    pass


async def get_db() -> AsyncSession:
    """获取数据库会话（用于依赖注入）"""
    async with AsyncSessionLocal() as session:
        yield session


async def init_db():
    """初始化数据库（创建所有表）"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
