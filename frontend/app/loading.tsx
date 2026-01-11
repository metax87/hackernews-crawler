'use client';

import { Layout, Card, Skeleton, Row, Col, Space } from 'antd';

const { Header, Content, Footer } = Layout;

export default function Loading() {
  return (
    <Layout style={{ minHeight: '100vh' }}>
      {/* Header 骨架 */}
      <Header
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '0 50px',
        }}
      >
        <Skeleton.Button active size="large" style={{ width: 180 }} />
        <Skeleton.Avatar active size="large" shape="circle" />
      </Header>

      <Content style={{ padding: '24px 50px' }}>
        <div style={{ maxWidth: 1200, margin: '0 auto' }}>
          {/* 统计卡片骨架 */}
          <Card style={{ marginBottom: 24 }}>
            <Row gutter={16}>
              {[1, 2, 3, 4].map((item) => (
                <Col xs={24} sm={12} md={6} key={item}>
                  <Skeleton active paragraph={{ rows: 1 }} />
                </Col>
              ))}
            </Row>
            <div style={{ marginTop: 16 }}>
              <Skeleton.Button active size="large" style={{ width: 120 }} />
            </div>
          </Card>

          {/* 搜索和筛选骨架 */}
          <Card style={{ marginBottom: 24 }}>
            <Space direction="vertical" style={{ width: '100%' }} size="large">
              <Skeleton.Input active size="large" block />
              <Space wrap>
                <Skeleton.Button active size="default" style={{ width: 100 }} />
                <Skeleton.Button active size="default" style={{ width: 100 }} />
              </Space>
            </Space>
          </Card>

          {/* 表格骨架 */}
          <Card>
            <Skeleton active paragraph={{ rows: 8 }} />
          </Card>
        </div>
      </Content>

      <Footer style={{ textAlign: 'center' }}>
        <Skeleton.Input active size="small" style={{ width: 300 }} />
      </Footer>
    </Layout>
  );
}
