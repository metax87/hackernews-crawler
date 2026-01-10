# 项目规划 - HN AI Stories 数据服务

## 产品愿景

将 Hacker News 爬虫升级为完整的数据服务，提供 REST API 供前端调用，支持 AI 相关故事的持久化存储和查询。

## 技术选型

| 层级 | 技术 | 选择理由 |
|------|------|----------|
| HTTP 客户端 | httpx | 支持异步，API 与 requests 相似 |
| 配置管理 | pydantic-settings | FastAPI 生态，类型安全 |
| Web 框架 | FastAPI | 自动文档、类型安全、异步支持 |
| ORM | SQLAlchemy 2.0 | Python 标准，支持类型提示 |
| 数据库 | PostgreSQL | 最流行开源关系数据库 |
| 容器化 | Docker Compose | 本地开发标准方案 |

---

## 阶段规划

### 阶段 1：修复问题 + 配置管理 ✅

**目标**：让爬虫代码更健壮、可配置

**完成内容**：
- [x] 启用 SSL 验证（httpx 替换 requests）
- [x] 配置外置（pydantic-settings + .env）
- [x] 错误处理增强（tenacity 重试）
- [x] 日志系统（logging 模块）
- [x] 模块化重构（app 目录结构）

**产出文件**：
- `app/config.py` - 配置管理
- `app/services/crawler.py` - 爬虫服务
- `.env.example` - 配置模板

---

### 阶段 2：PostgreSQL 集成

**目标**：数据持久化，支持查询

**计划内容**：
- [ ] 定义 Story 数据模型
- [ ] 配置数据库连接（asyncpg）
- [ ] 实现数据去重（hn_id 唯一约束）
- [ ] Alembic 数据库迁移

**数据模型设计**：
```python
class Story(Base):
    __tablename__ = "stories"

    id: int              # 主键
    hn_id: int           # HN 原始 ID（唯一索引）
    title: str
    url: str | None
    score: int
    author: str
    posted_at: datetime
    comments_count: int
    is_ai_related: bool  # 索引
    created_at: datetime # 入库时间
```

**新增依赖**：
- sqlalchemy[asyncio]
- asyncpg
- alembic

---

### 阶段 3：FastAPI 接口

**目标**：提供 REST API 给前端

**API 设计**：
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/stories` | 分页获取故事（支持筛选）|
| GET | `/api/stories/{id}` | 获取单个故事 |
| POST | `/api/crawl` | 手动触发爬取 |
| GET | `/api/stats` | 统计信息 |
| GET | `/health` | 健康检查 |

**查询参数**：
- `page`, `size` - 分页
- `ai_only` - 只看 AI 相关
- `min_score` - 最低分数
- `sort_by` - 排序字段

**新增依赖**：
- fastapi
- uvicorn

---

### 阶段 4：Docker 化

**目标**：一键启动完整环境

**docker-compose.yml**：
```yaml
services:
  api:
    build: .
    ports: ["8000:8000"]
    depends_on: [db]
    environment:
      - DATABASE_URL=postgresql+asyncpg://...

  db:
    image: postgres:16
    volumes:
      - pgdata:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=hackernews
      - POSTGRES_USER=hn
      - POSTGRES_PASSWORD=secret
```

**新增文件**：
- `Dockerfile`
- `docker-compose.yml`

---

## 可选扩展（后续考虑）

| 功能 | 说明 | 优先级 |
|------|------|--------|
| 定时爬取 | APScheduler 自动更新 | 中 |
| 数据分析 | 热度趋势、词云 | 低 |
| 邮件推送 | 每日 AI 热点摘要 | 低 |
| 多数据源 | Reddit、Twitter | 低 |

---

## 目录结构（最终）

```
hackernews-crawler/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 入口
│   ├── config.py            # 配置管理
│   ├── database.py          # 数据库连接
│   ├── models.py            # SQLAlchemy 模型
│   ├── schemas.py           # Pydantic 模型
│   ├── api/
│   │   ├── __init__.py
│   │   └── stories.py       # 故事路由
│   └── services/
│       ├── __init__.py
│       └── crawler.py       # 爬虫服务
├── alembic/                 # 数据库迁移
├── tests/
├── .env.example
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── CLAUDE.md
└── ROADMAP.md
```
