"""
Hacker News 爬虫服务

改进点：
1. 使用 httpx 替代 requests（支持异步）
2. 配置外置（从 config.py 读取）
3. 添加重试机制（tenacity）
4. 结构化日志
5. 启用 SSL 验证
6. 数据库持久化（阶段 2）
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Optional

import httpx
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import settings
from app.database import AsyncSessionLocal
from app.models import Story

# 配置日志
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class HNScraper:
    """Hacker News 爬虫"""

    def __init__(self):
        self.base_url = settings.hn_api_base
        self.timeout = settings.request_timeout
        self.client = httpx.Client(timeout=self.timeout)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.client.close()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
    )
    def _get(self, url: str) -> dict | list | None:
        """带重试的 GET 请求"""
        response = self.client.get(url)
        response.raise_for_status()
        return response.json()

    def fetch_top_stories(self, limit: int | None = None) -> list[int]:
        """获取热门故事 ID 列表"""
        limit = limit or settings.fetch_limit
        url = f"{self.base_url}/topstories.json"

        logger.info(f"获取热门故事列表，限制 {limit} 条")
        story_ids = self._get(url)
        return story_ids[:limit]

    def fetch_story_detail(self, story_id: int) -> dict | None:
        """获取单个故事详情"""
        url = f"{self.base_url}/item/{story_id}.json"

        try:
            return self._get(url)
        except Exception as e:
            logger.warning(f"获取故事 {story_id} 失败: {e}")
            return None

    def filter_ai_stories(self, stories: list[dict]) -> list[dict]:
        """筛选 AI 相关故事"""
        keywords = settings.ai_keywords_list

        ai_stories = []
        for story in stories:
            title = story.get("title", "").lower()
            if any(kw in title for kw in keywords):
                ai_stories.append(story)

        logger.info(f"筛选出 {len(ai_stories)}/{len(stories)} 个 AI 相关故事")
        return ai_stories

    def crawl(self, limit: int | None = None) -> list[dict]:
        """执行爬取流程"""
        logger.info("开始爬取 Hacker News...")

        # 1. 获取故事 ID
        story_ids = self.fetch_top_stories(limit)
        logger.info(f"获取到 {len(story_ids)} 个故事 ID")

        # 2. 获取详情
        stories = []
        for i, story_id in enumerate(story_ids, 1):
            logger.debug(f"获取第 {i}/{len(story_ids)} 个故事...")
            story = self.fetch_story_detail(story_id)

            if story and story.get("type") == "story":
                stories.append(
                    {
                        "hn_id": story_id,
                        "title": story.get("title"),
                        "url": story.get("url"),
                        "score": story.get("score", 0),
                        "author": story.get("by"),
                        "posted_at": story.get("time"),
                        "comments_count": story.get("descendants", 0),
                        "hn_url": f"https://news.ycombinator.com/item?id={story_id}",
                    }
                )

        logger.info(f"成功获取 {len(stories)} 个故事详情")

        # 3. 筛选 AI 相关
        ai_stories = self.filter_ai_stories(stories)

        return ai_stories


def save_to_json(data: list[dict], filename: str | None = None) -> str:
    """保存数据到 JSON 文件"""
    os.makedirs(settings.data_dir, exist_ok=True)

    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"hn_ai_stories_{timestamp}.json"

    filepath = os.path.join(settings.data_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    logger.info(f"数据已保存到 {filepath}")
    return filepath


async def save_to_database(stories: list[dict]) -> tuple[int, int]:
    """
    保存故事到数据库

    返回：(新增数量, 更新数量)
    """
    added = 0
    updated = 0

    async with AsyncSessionLocal() as session:
        for story_data in stories:
            # 检查是否已存在
            stmt = select(Story).where(Story.hn_id == story_data["hn_id"])
            result = await session.execute(stmt)
            existing_story = result.scalar_one_or_none()

            if existing_story:
                # 更新现有记录（分数和评论数可能变化）
                existing_story.score = story_data["score"]
                existing_story.comments_count = story_data["comments_count"]
                updated += 1
                logger.debug(f"更新故事: {story_data['hn_id']}")
            else:
                # 创建新记录
                story = Story(
                    hn_id=story_data["hn_id"],
                    title=story_data["title"],
                    url=story_data.get("url"),
                    author=story_data["author"],
                    score=story_data["score"],
                    comments_count=story_data["comments_count"],
                    posted_at=datetime.fromtimestamp(story_data["posted_at"]),
                    is_ai_related=True,  # 已筛选过的都是 AI 相关
                    hn_url=story_data["hn_url"],
                )
                session.add(story)
                added += 1
                logger.debug(f"新增故事: {story_data['hn_id']}")

        await session.commit()

    logger.info(f"数据库保存完成: 新增 {added} 条, 更新 {updated} 条")
    return added, updated


def run_crawler():
    """运行爬虫的入口函数（同步版本，仅保存 JSON）"""
    with HNScraper() as scraper:
        stories = scraper.crawl()
        save_to_json(stories)

        # 显示结果
        print(f"\n找到 {len(stories)} 个 AI 相关故事：")
        for story in stories[:5]:
            print(f"  - {story['title']} (score: {story['score']})")

        if len(stories) > 5:
            print(f"  ... 还有 {len(stories) - 5} 条")


async def run_crawler_async():
    """运行爬虫的入口函数（异步版本，保存到数据库）"""
    with HNScraper() as scraper:
        stories = scraper.crawl()

        # 保存到数据库
        added, updated = await save_to_database(stories)

        # 也保存 JSON 备份
        save_to_json(stories)

        # 显示结果
        print(f"\n找到 {len(stories)} 个 AI 相关故事：")
        print(f"数据库: 新增 {added} 条, 更新 {updated} 条")
        print("\n最新故事:")
        for story in stories[:5]:
            print(f"  - {story['title']} (score: {story['score']})")

        if len(stories) > 5:
            print(f"  ... 还有 {len(stories) - 5} 条")


if __name__ == "__main__":
    # 使用异步版本
    asyncio.run(run_crawler_async())
