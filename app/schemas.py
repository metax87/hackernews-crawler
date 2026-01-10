"""
Pydantic 模型定义

用于数据验证、序列化和 API 响应。
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class StoryBase(BaseModel):
    """Story 基础模型"""

    hn_id: int = Field(..., description="HN 原始 ID")
    title: str = Field(..., max_length=500, description="故事标题")
    url: Optional[str] = Field(None, max_length=1000, description="原文链接")
    author: str = Field(..., max_length=100, description="作者")
    score: int = Field(default=0, ge=0, description="热度分数")
    comments_count: int = Field(default=0, ge=0, description="评论数")
    posted_at: datetime = Field(..., description="HN 发布时间")
    is_ai_related: bool = Field(default=False, description="是否 AI 相关")
    hn_url: str = Field(..., max_length=200, description="HN 讨论链接")


class StoryCreate(StoryBase):
    """创建 Story 时使用"""

    pass


class StoryUpdate(BaseModel):
    """更新 Story 时使用"""

    score: Optional[int] = None
    comments_count: Optional[int] = None


class StoryInDB(StoryBase):
    """数据库中的 Story（包含 ID 和时间戳）"""

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)  # 允许从 ORM 对象创建
