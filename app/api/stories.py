"""
Stories API 路由

提供故事的查询、统计等接口。
"""

from __future__ import annotations

import asyncio
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import Integer, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models import Story
from app.schemas import StoryInDB
from app.services.crawler import HNScraper, save_to_database, save_to_json

router = APIRouter()


# 依赖注入：获取数据库会话
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


@router.get("/stories", response_model=dict)
async def get_stories(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    ai_only: bool = Query(True, description="只返回 AI 相关"),
    min_score: Optional[int] = Query(None, ge=0, description="最低分数"),
    db: AsyncSession = Depends(get_db),
):
    """
    获取故事列表（分页）

    参数:
    - page: 页码（从1开始）
    - size: 每页数量（1-100）
    - ai_only: 是否只返回 AI 相关故事
    - min_score: 最低分数筛选
    """
    # 构建查询
    query = select(Story)

    if ai_only:
        query = query.where(Story.is_ai_related == True)

    if min_score is not None:
        query = query.where(Story.score >= min_score)

    # 按分数降序
    query = query.order_by(Story.score.desc())

    # 获取总数
    count_query = select(func.count()).select_from(query.subquery())
    result = await db.execute(count_query)
    total = result.scalar()

    # 分页
    offset = (page - 1) * size
    query = query.offset(offset).limit(size)

    # 执行查询
    result = await db.execute(query)
    stories = result.scalars().all()

    return {
        "items": [StoryInDB.model_validate(story) for story in stories],
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size,  # 向上取整
    }


@router.get("/stories/{story_id}", response_model=StoryInDB)
async def get_story(
    story_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    获取单个故事详情

    参数:
    - story_id: 故事 ID（数据库主键）
    """
    stmt = select(Story).where(Story.id == story_id)
    result = await db.execute(stmt)
    story = result.scalar_one_or_none()

    if not story:
        raise HTTPException(status_code=404, detail="Story not found")

    return StoryInDB.model_validate(story)


@router.get("/stats", response_model=dict)
async def get_stats(db: AsyncSession = Depends(get_db)):
    """
    获取统计信息

    返回:
    - total: 总故事数
    - ai_count: AI 相关故事数
    - avg_score: 平均分数
    - top_score: 最高分数
    """
    # 总数和 AI 数量
    stmt = select(
        func.count(Story.id).label("total"),
        func.sum(func.cast(Story.is_ai_related, Integer)).label("ai_count"),
    )
    result = await db.execute(stmt)
    row = result.one()

    # 平均分数和最高分数
    stmt = select(
        func.avg(Story.score).label("avg_score"),
        func.max(Story.score).label("top_score"),
    )
    result = await db.execute(stmt)
    stats = result.one()

    return {
        "total": row.total or 0,
        "ai_count": row.ai_count or 0,
        "avg_score": round(stats.avg_score, 1) if stats.avg_score else 0,
        "top_score": stats.top_score or 0,
    }


@router.post("/crawl", response_model=dict)
async def trigger_crawl():
    """
    手动触发爬取

    这是一个后台任务，会立即返回，爬取在后台进行。
    """

    async def run_crawler():
        """后台运行爬虫"""
        with HNScraper() as scraper:
            stories = scraper.crawl()
            added, updated = await save_to_database(stories)
            save_to_json(stories)
            return {"added": added, "updated": updated, "total": len(stories)}

    # 启动后台任务
    asyncio.create_task(run_crawler())

    return {
        "message": "爬取任务已启动",
        "status": "running",
    }
