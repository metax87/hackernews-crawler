'use client';

import { useEffect, useState } from 'react';
import { List, Card, Tag, Space, Statistic, Row, Col, Button, message, Spin } from 'antd';
import { FireOutlined, CommentOutlined, ClockCircleOutlined, ReloadOutlined } from '@ant-design/icons';
import { fetchStories, fetchStats, triggerCrawl, type Story, type StatsResponse } from '@/lib/api';

export default function StoryList() {
  const [stories, setStories] = useState<Story[]>([]);
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [crawling, setCrawling] = useState(false);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 20,
    total: 0,
  });

  // 加载故事列表
  const loadStories = async (page = 1, pageSize = 20) => {
    try {
      setLoading(true);
      const data = await fetchStories({ page, size: pageSize, ai_only: true });
      setStories(data.items);
      setPagination({
        current: page,
        pageSize,
        total: data.total,
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
            <Col span={6}>
              <Statistic title="总故事数" value={stats.total} />
            </Col>
            <Col span={6}>
              <Statistic title="AI 相关" value={stats.ai_count} />
            </Col>
            <Col span={6}>
              <Statistic
                title="平均分数"
                value={stats.avg_score}
                precision={1}
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="最高分数"
                value={stats.top_score}
                prefix={<FireOutlined />}
              />
            </Col>
          </Row>
          <div style={{ marginTop: 16 }}>
            <Button
              type="primary"
              icon={<ReloadOutlined />}
              loading={crawling}
              onClick={handleCrawl}
            >
              手动爬取
            </Button>
          </div>
        </Card>
      )}

      {/* 故事列表 */}
      <Spin spinning={loading}>
        <List
          itemLayout="vertical"
          size="large"
          pagination={{
            ...pagination,
            onChange: (page, pageSize) => {
              loadStories(page, pageSize);
            },
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 条`,
          }}
          dataSource={stories}
          renderItem={(story) => (
            <List.Item
              key={story.id}
              extra={
                <Space direction="vertical" align="end">
                  <Tag color="volcano" icon={<FireOutlined />}>
                    {story.score}
                  </Tag>
                  <Tag icon={<CommentOutlined />}>
                    {story.comments_count}
                  </Tag>
                </Space>
              }
            >
              <List.Item.Meta
                title={
                  <a
                    href={story.url || story.hn_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{ fontSize: 18, fontWeight: 500 }}
                  >
                    {story.title}
                  </a>
                }
                description={
                  <Space size="large">
                    <span>
                      <ClockCircleOutlined /> {formatTime(story.posted_at)}
                    </span>
                    <span>作者：{story.author}</span>
                    <a
                      href={story.hn_url}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      HN 讨论
                    </a>
                  </Space>
                }
              />
            </List.Item>
          )}
        />
      </Spin>
    </div>
  );
}
