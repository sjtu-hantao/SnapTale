import React from 'react';
import { Layout, Space, theme } from 'antd';
import MenuButton from './MenuButton/MenuButton';
import { ReactComponent as MyIcon } from '../assets/logo.svg';

const { Header, Content, Footer } = Layout;

interface MyLayoutProps {
  children: React.ReactNode;
}

const MyLayout: React.FC<MyLayoutProps> = ({ children }) => {
  const {
    token: { colorBgContainer, borderRadiusLG, colorPrimary },
  } = theme.useToken();

  // TODO: Manage breadcrumb items dynamically with React Context
  // const breadCrumbItems = [
  //   {
  //     title: 'Home',
  //     href: '/',
  //   },
  //   {
  //     title: 'Profile',
  //   },
  // ]

  return (
    <Layout >
      <Header style={{ display: 'flex', alignItems: 'center' }}>
        <a href="/" style={{ color: 'white', fontSize: 24, fontFamily: 'cursive', fontWeight: 'bold' }}>
         <Space><MyIcon style={{ height: '10vh' }}/> SnapTale
          </Space>
        </a>
      </Header>
      <Content style={{ padding: '0 24px',
        margin: '5px 0' , backgroundColor: '#F0F2F5',
       }}>
        <div
          style={{
            background: colorBgContainer,
            minHeight: '90vh',
            padding: 24,
            borderRadius: borderRadiusLG,
          }}
        >
          {children}
        </div>
      </Content>
      <Footer style={{ textAlign: 'center', backgroundColor: '#F0F2F5'  }}>
        Ant Design ©{new Date().getFullYear()} Created by Ant UED
      </Footer>
      <MenuButton />
    </Layout>
  );
};

export default MyLayout;