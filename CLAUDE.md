# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

Hacker News 爬虫项目，用于抓取热门故事并筛选出 AI 相关内容。目标是逐步升级为完整的数据服务。

**技术栈**:
- Python 3.9+
- FastAPI（Web 框架）
- SQLAlchemy 2.0（异步 ORM）
- httpx（HTTP 请求）
- pydantic-settings（配置管理）
- SQLite/PostgreSQL（数据库）

## 核心命令

```bash
# 安装依赖
python3 -m pip install -r requirements.txt

# 运行爬虫（保存到数据库）
python3 -m app.services.crawler

# 启动 API 服务器
python3 -m uvicorn app.main:app --reload
# 访问 http://localhost:8000/docs 查看 API 文档
```

## 代码架构

```
app/
├── main.py             # FastAPI 应用入口
├── config.py           # 配置管理
├── database.py         # 数据库连接
├── models.py           # SQLAlchemy 数据模型
├── schemas.py          # Pydantic 验证模型
├── api/
│   └── stories.py      # Stories API 路由
└── services/
    └── crawler.py      # 爬虫服务
```

**核心类 `HNScraper`** (`app/services/crawler.py`):
- `fetch_top_stories()` - 获取热门故事 ID
- `fetch_story_detail()` - 获取单个故事详情（带重试）
- `filter_ai_stories()` - AI 关键词筛选
- `crawl()` - 编排完整流程

**配置项** (`.env` 或环境变量):
- `FETCH_LIMIT` - 获取故事数量（默认 30）
- `AI_KEYWORDS` - 逗号分隔的关键词列表
- `LOG_LEVEL` - 日志级别

## HN API 端点

- Top Stories: `https://hacker-news.firebaseio.com/v0/topstories.json`
- Item Detail: `https://hacker-news.firebaseio.com/v0/item/{id}.json`

## 输出格式

```json
{
  "hn_id": 12345,
  "title": "标题",
  "url": "原文链接",
  "score": 123,
  "author": "作者",
  "posted_at": 1234567890,
  "comments_count": 45,
  "hn_url": "HN 讨论链接"
}
```

---

## 开发进度

### 阶段 1：修复问题 + 配置管理 ✅

**完成时间**: 2026-01-10

**解决的问题**:
| 原问题 | 解决方案 |
|--------|----------|
| SSL 验证禁用 | 改用 httpx，默认启用 SSL |
| 硬编码参数 | pydantic-settings + .env 配置 |
| 错误处理不完整 | tenacity 自动重试（3次，指数退避）|
| 无日志系统 | logging 模块，可配置级别 |
| 单文件结构 | 拆分为 app 模块化结构 |

**新增功能**:
- 配置外置：所有参数可通过 `.env` 文件或环境变量配置
- 请求重试：失败自动重试 3 次，间隔指数增长
- 结构化日志：记录每个 HTTP 请求和关键操作
- 上下文管理器：`HNScraper` 支持 `with` 语法，自动管理连接

**技术学习点**:
- `pydantic-settings`：类型安全的配置管理
- `httpx`：现代 HTTP 客户端，支持同步/异步
- `tenacity`：灵活的重试装饰器
- Python 模块化：`__init__.py` 和包结构

---

### 阶段 2：数据库集成 ✅

**完成时间**: 2026-01-10

**新增文件**:
| 文件 | 说明 |
|------|------|
| `app/database.py` | SQLAlchemy 异步引擎配置 |
| `app/models.py` | Story 数据模型（ORM） |
| `app/schemas.py` | Pydantic 数据验证模型 |
| `alembic/` | 数据库迁移管理 |

**数据模型设计**:
```python
class Story:
    id              # 主键
    hn_id           # HN ID（唯一索引）
    title, url      # 基本信息
    score, comments_count  # 统计
    posted_at       # HN 发布时间
    created_at, updated_at  # 入库/更新时间
    is_ai_related   # 分类标记（索引）
```

**核心功能**:
- ✅ SQLite 本地存储（默认）
- ✅ 数据去重（hn_id 唯一约束）
- ✅ 自动更新（分数、评论数）
- ✅ Alembic 迁移管理
- ✅ 异步数据库操作

**技术学习点**:
- `SQLAlchemy 2.0`：异步 ORM，类型安全的 Mapped
- `Alembic`：数据库版本控制
- `asyncio`：Python 异步编程
- 数据库索引设计：复合索引优化查询

**数据库命令**:
```bash
# 创建迁移
python3 -m alembic revision --autogenerate -m "描述"

# 执行迁移
python3 -m alembic upgrade head

# 查询数据
sqlite3 data/hackernews.db "SELECT * FROM stories;"
```

---

### 阶段 3：FastAPI 接口 ✅

**完成时间**: 2026-01-10

**新增文件**:
| 文件 | 说明 |
|------|------|
| `app/main.py` | FastAPI 应用入口 |
| `app/api/stories.py` | Stories API 路由 |

**API 端点**:
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 根路径信息 |
| GET | `/health` | 健康检查 |
| GET | `/docs` | API 文档（自动生成）|
| GET | `/api/stories` | 获取故事列表（分页）|
| GET | `/api/stories/{id}` | 获取单个故事 |
| GET | `/api/stats` | 获取统计信息 |
| POST | `/api/crawl` | 手动触发爬取 |

**查询参数**（GET /api/stories）:
- `page` - 页码（默认 1）
- `size` - 每页数量（默认 20，最大 100）
- `ai_only` - 只返回 AI 相关（默认 true）
- `min_score` - 最低分数筛选

**核心功能**:
- ✅ RESTful API 设计
- ✅ 自动 API 文档（Swagger UI）
- ✅ 分页查询
- ✅ 数据筛选（分数、AI 分类）
- ✅ CORS 支持（允许前端跨域）
- ✅ 统计接口

**技术学习点**:
- `FastAPI`：现代 Python Web 框架
- 自动文档生成：基于 OpenAPI 规范
- 依赖注入：数据库会话管理
- 异步路由：async/await 异步处理
- Pydantic 验证：自动请求/响应验证

**运行命令**:
```bash
# 启动 API 服务器
python3 -m uvicorn app.main:app --reload

# 或者
python3 -m app.main

# 访问 API 文档
open http://localhost:8000/docs
```

---

### 阶段 4：Docker 化 ⏳

详见 [ROADMAP.md](./ROADMAP.md)
