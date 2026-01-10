"""
数据库模型定义

使用 SQLAlchemy 2.0 的 Mapped 类型注解。
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, Boolean, Index, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Story(Base):
    """Hacker News 故事模型"""

    __tablename__ = "stories"

    # 主键
    id: Mapped[int] = mapped_column(primary_key=True)

    # HN 原始 ID（唯一索引，防止重复）
    hn_id: Mapped[int] = mapped_column(Integer, unique=True, index=True, nullable=False)

    # 基本信息
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    author: Mapped[str] = mapped_column(String(100), nullable=False)

    # 统计信息
    score: Mapped[int] = mapped_column(Integer, default=0)
    comments_count: Mapped[int] = mapped_column(Integer, default=0)

    # 时间信息
    posted_at: Mapped[datetime] = mapped_column(nullable=False)  # HN 发布时间
    created_at: Mapped[datetime] = mapped_column(
        default=func.now(), nullable=False
    )  # 入库时间
    updated_at: Mapped[datetime] = mapped_column(
        default=func.now(), onupdate=func.now(), nullable=False
    )  # 更新时间

    # 分类标记
    is_ai_related: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    # HN 讨论链接
    hn_url: Mapped[str] = mapped_column(String(200), nullable=False)

    # 复合索引（常用查询优化）
    __table_args__ = (
        Index("idx_ai_score", "is_ai_related", "score"),  # AI 故事按分数查询
        Index("idx_posted_at", "posted_at"),  # 按发布时间查询
    )

    def __repr__(self) -> str:
        return f"<Story(hn_id={self.hn_id}, title={self.title[:30]}...)>"
