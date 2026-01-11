# HN AI Stories - 前端

基于 Next.js + Ant Design 的 Hacker News AI 故事展示界面。

## 技术栈

- Next.js 16 + TypeScript
- Ant Design 5
- Tailwind CSS

## 快速开始

### 1. 安装依赖

```bash
npm install
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env.local`：

```bash
cp .env.example .env.local
```

默认配置：
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. 启动开发服务器

```bash
npm run dev
```

访问 http://localhost:3000

## 功能特性

- ✅ 故事列表展示（分页）
- ✅ 统计数据面板
- ✅ 手动触发爬取
- ✅ 响应式设计
- ✅ 时间格式化显示

## API 集成

前端通过 `lib/api.ts` 调用后端 API：

- `GET /api/stories` - 获取故事列表
- `GET /api/stories/{id}` - 获取单个故事
- `GET /api/stats` - 获取统计信息
- `POST /api/crawl` - 触发爬取

## 项目结构

```
frontend/
├── app/
│   ├── page.tsx          # 首页
│   ├── layout.tsx        # 布局
│   └── globals.css       # 全局样式
├── components/
│   └── StoryList.tsx     # 故事列表组件
├── lib/
│   └── api.ts            # API 调用工具
└── .env.example          # 环境变量模板
```

## 构建生产版本

```bash
npm run build
npm start
```

## 注意事项

- 确保后端 API 服务已启动（http://localhost:8000）
- 如果端口冲突，Next.js 会自动使用下一个可用端口
