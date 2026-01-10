"""
FastAPI 应用入口

HN AI Stories 数据服务 API
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import stories
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    print("🚀 HN AI Stories API 启动")
    yield
    # 关闭时
    print("👋 HN AI Stories API 关闭")


# 创建 FastAPI 应用
app = FastAPI(
    title="HN AI Stories API",
    description="Hacker News AI 相关故事数据服务",
    version="0.2.0",
    lifespan=lifespan,
)

# 配置 CORS（允许前端跨域访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该指定具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(stories.router, prefix="/api", tags=["Stories"])


@app.get("/", tags=["Root"])
async def root():
    """根路径"""
    return {
        "message": "HN AI Stories API",
        "version": "0.2.0",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health():
    """健康检查"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # 开发环境自动重载
    )
