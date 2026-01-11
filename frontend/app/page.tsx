'use client';

import { Layout, Typography } from 'antd';
import StoryList from '@/components/StoryList';

const { Header, Content, Footer } = Layout;
const { Title } = Typography;

export default function Home() {
  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{
        display: 'flex',
        alignItems: 'center',
        background: '#fff',
        borderBottom: '1px solid #f0f0f0'
      }}>
        <Title level={3} style={{ margin: 0, color: '#ff6600' }}>
          🔥 HN AI Stories
        </Title>
      </Header>

      <Content style={{ padding: '24px 50px' }}>
        <div style={{ maxWidth: 1200, margin: '0 auto' }}>
          <StoryList />
        </div>
      </Content>

      <Footer style={{ textAlign: 'center' }}>
        HN AI Stories ©2026 | Powered by Hacker News API
      </Footer>
    </Layout>
  );
}
