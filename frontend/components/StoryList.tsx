'use client';

import { useEffect, useState } from 'react';
import {
  Table,
  Card,
  Tag,
  Space,
  Statistic,
  Row,
  Col,
  Button,
  App,
  Spin,
  Input,
  Select,
  Slider,
  Typography,
} from 'antd';
import type { TableProps } from 'antd';
import {
  FireOutlined,
  CommentOutlined,
  ClockCircleOutlined,
  ReloadOutlined,
  SearchOutlined,
  FilterOutlined,
} from '@ant-design/icons';
import { fetchStories, fetchStats, triggerCrawl, type Story, type StatsResponse } from '@/lib/api';

const { Search } = Input;
const { Link } = Typography;

export default function StoryList() {
  const { message } = App.useApp();
  const [stories, setStories] = useState<Story[]>([]);
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [crawling, setCrawling] = useState(false);
  const [searchText, setSearchText] = useState('');
  const [minScore, setMinScore] = useState(0);
  const [showFilters, setShowFilters] = useState(false);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 20,
    total: 0,
  });

  // Table 列定义
  const columns: TableProps<Story>['columns'] = [
    {
      title: '标题',
      dataIndex: 'title',
      key: 'title',
      width: '50%',
      render: (text, record) => (
        <div>
          <a
            href={record.url || record.hn_url}
            target="_blank"
            rel="noopener noreferrer"
            style={{ fontSize: 16, fontWeight: 500, color: '#1890ff' }}
          >
            {text}
          </a>
          <div style={{ marginTop: 8, fontSize: 13, color: '#8c8c8c' }}>
            <Space size="large" wrap>
              <span>
                <ClockCircleOutlined /> {formatTime(record.posted_at)}
              </span>
              <span>作者: {record.author}</span>
              <a href={record.hn_url} target="_blank" rel="noopener noreferrer">
                HN 讨论
              </a>
            </Space>
          </div>
        </div>
      ),
    },
    {
      title: '分数',
      dataIndex: 'score',
      key: 'score',
      width: 100,
      align: 'center',
      sorter: (a, b) => a.score - b.score,
      render: (score) => (
        <Tag color="volcano" icon={<FireOutlined />} style={{ fontSize: 14 }}>
          {score}
        </Tag>
      ),
    },
    {
      title: '评论',
      dataIndex: 'comments_count',
      key: 'comments_count',
      width: 100,
      align: 'center',
      sorter: (a, b) => a.comments_count - b.comments_count,
      render: (count) => (
        <Tag icon={<CommentOutlined />} style={{ fontSize: 14 }}>
          {count}
        </Tag>
      ),
    },
  ];

  // 加载故事列表
  const loadStories = async (page = 1, pageSize = 20, search = searchText, scoreFilter = minScore) => {
    try {
      setLoading(true);
      const data = await fetchStories({
        page,
        size: pageSize,
        ai_only: true,
        min_score: scoreFilter > 0 ? scoreFilter : undefined,
      });

      // 客户端搜索过滤
      let filteredItems = data.items;
      if (search) {
        const searchLower = search.toLowerCase();
        filteredItems = data.items.filter(
          (story) =>
            story.title.toLowerCase().includes(searchLower) ||
            story.author.toLowerCase().includes(searchLower)
        );
      }

      setStories(filteredItems);
      setPagination({
        current: page,
        pageSize,
        total: search ? filteredItems.length : data.total,
      });
    } catch (error) {
      message.error('加载故事失败');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  // 加载统计信息
  const loadStats = async () => {
    try {
      const data = await fetchStats();
      setStats(data);
    } catch (error) {
      console.error('加载统计失败:', error);
    }
  };

  // 触发爬取
  const handleCrawl = async () => {
    try {
      setCrawling(true);
      await triggerCrawl();
      message.success('爬取任务已启动，请稍后刷新查看新数据');

      // 5 秒后刷新数据
      setTimeout(() => {
        loadStories(pagination.current, pagination.pageSize);
        loadStats();
      }, 5000);
    } catch (error) {
      message.error('触发爬取失败');
      console.error(error);
    } finally {
      setCrawling(false);
    }
  };

  // 搜索处理
  const handleSearch = (value: string) => {
    setSearchText(value);
    setPagination({ ...pagination, current: 1 });
    loadStories(1, pagination.pageSize, value, minScore);
  };

  // 分数筛选
  const handleScoreFilter = (value: number) => {
    setMinScore(value);
    setPagination({ ...pagination, current: 1 });
    loadStories(1, pagination.pageSize, searchText, value);
  };

  // 重置筛选
  const handleReset = () => {
    setSearchText('');
    setMinScore(0);
    setPagination({ ...pagination, current: 1 });
    loadStories(1, pagination.pageSize, '', 0);
  };

  // 格式化时间
  const formatTime = (timeStr: string) => {
    const date = new Date(timeStr);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const hours = Math.floor(diff / 1000 / 60 / 60);
    const days = Math.floor(hours / 24);

    if (days > 0) return `${days} 天前`;
    if (hours > 0) return `${hours} 小时前`;
    return '刚刚';
  };

  useEffect(() => {
    loadStories();
    loadStats();
  }, []);

  return (
    <div>
      {/* 统计卡片 */}
      {stats && (
        <Card style={{ marginBottom: 24 }}>
          <Row gutter={16}>
            <Col xs={24} sm={12} md={6}>
              <Statistic title="总故事数" value={stats.total} />
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Statistic title="AI 相关" value={stats.ai_count} />
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Statistic title="平均分数" value={stats.avg_score} precision={1} />
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Statistic title="最高分数" value={stats.top_score} prefix={<FireOutlined />} />
            </Col>
          </Row>
          <div style={{ marginTop: 16 }}>
            <Button type="primary" icon={<ReloadOutlined />} loading={crawling} onClick={handleCrawl}>
              手动爬取
            </Button>
          </div>
        </Card>
      )}

      {/* 搜索和筛选 */}
      <Card style={{ marginBottom: 24 }}>
        <Space vertical style={{ width: '100%' }} size="large">
          <Search
            placeholder="搜索标题或作者..."
            allowClear
            enterButton={<SearchOutlined />}
            size="large"
            onSearch={handleSearch}
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
          />

          <Space wrap>
            <Button
              icon={<FilterOutlined />}
              onClick={() => setShowFilters(!showFilters)}
            >
              {showFilters ? '隐藏筛选' : '高级筛选'}
            </Button>

            {(searchText || minScore > 0) && (
              <Button onClick={handleReset}>重置筛选</Button>
            )}

            {minScore > 0 && (
              <Tag color="blue" closable onClose={() => handleScoreFilter(0)}>
                分数 ≥ {minScore}
              </Tag>
            )}
          </Space>

          {showFilters && (
            <Card size="small" style={{ background: '#fafafa' }}>
              <Space vertical style={{ width: '100%' }}>
                <div>
                  <div style={{ marginBottom: 8 }}>
                    <FireOutlined /> 最低分数: {minScore}
                  </div>
                  <Slider
                    min={0}
                    max={500}
                    step={10}
                    value={minScore}
                    onChange={setMinScore}
                    onAfterChange={handleScoreFilter}
                    marks={{
                      0: '0',
                      100: '100',
                      200: '200',
                      300: '300',
                      500: '500+',
                    }}
                  />
                </div>
              </Space>
            </Card>
          )}
        </Space>
      </Card>

      {/* 故事列表 */}
      <Table<Story>
        columns={columns}
        dataSource={stories}
        loading={loading}
        rowKey="id"
        pagination={{
          ...pagination,
          onChange: (page, pageSize) => {
            loadStories(page, pageSize);
          },
          showSizeChanger: true,
          showTotal: (total) => `共 ${total} 条`,
        }}
      />
    </div>
  );
}
