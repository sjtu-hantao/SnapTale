import React from "react";
import { Layout, Space, Typography } from "antd";
import { Link, useLocation } from "react-router-dom";

const { Header, Content } = Layout;
const { Text, Title } = Typography;

interface AppShellProps {
  children: React.ReactNode;
  username: string;
}

const AppShell: React.FC<AppShellProps> = ({ children, username }) => {
  const location = useLocation();

  return (
    <Layout className="app-shell">
      <Header className="app-header">
        <div>
          <Title level={3} className="brand-title">
            SnapTale Studio
          </Title>
          <Text className="brand-subtitle">Agent-native social storytelling MVP</Text>
        </div>
        <Space size={24} align="center">
          <Link className={location.pathname === "/" ? "nav-link active" : "nav-link"} to="/">
            Create
          </Link>
          <Link
            className={location.pathname.startsWith("/growth") ? "nav-link active" : "nav-link"}
            to="/growth"
          >
            Growth
          </Link>
          <div className="user-pill">{username}</div>
        </Space>
      </Header>
      <Content className="app-content">{children}</Content>
    </Layout>
  );
};

export default AppShell;
