'use client';

import { Layout, Typography, Button, Space } from 'antd';
import { BulbOutlined, BulbFilled } from '@ant-design/icons';
import StoryList from '@/components/StoryList';
import ThemeProvider, { useTheme } from '@/components/ThemeProvider';

const { Header, Content, Footer } = Layout;
const { Title } = Typography;

function PageContent() {
  const { themeMode, toggleTheme } = useTheme();

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          background: themeMode === 'dark' ? '#1f1f1f' : '#fff',
          borderBottom: '1px solid',
          borderColor: themeMode === 'dark' ? '#303030' : '#f0f0f0',
          padding: '0 50px',
        }}
      >
        <Title level={3} style={{ margin: 0, color: '#ff6600' }}>
          🔥 HN AI Stories
        </Title>

        <Button
          type="text"
          icon={themeMode === 'dark' ? <BulbFilled /> : <BulbOutlined />}
          onClick={toggleTheme}
          style={{ fontSize: 20 }}
        />
      </Header>

      <Content style={{ padding: '24px 50px' }}>
        <div style={{ maxWidth: 1200, margin: '0 auto' }}>
          <StoryList />
        </div>
      </Content>

      <Footer
        style={{
          textAlign: 'center',
          background: themeMode === 'dark' ? '#1f1f1f' : '#fafafa',
        }}
      >
        HN AI Stories ©2026 | Powered by Hacker News API
      </Footer>
    </Layout>
  );
}

export default function Home() {
  return (
    <ThemeProvider>
      <PageContent />
    </ThemeProvider>
  );
}
