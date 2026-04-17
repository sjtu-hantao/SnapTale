import React from 'react';
import MyLayout from '../../components/Layout';
import { Row, Col, Card } from 'antd';
import RecentEntriesView from './RecentEntriesView';
import ProfileView from './ProfileView';
import ActivityHeatmap from './ActivityHeatmap';




const HomeContent: React.FC = () => {
    return (
        <div>
        <Row gutter={24}>
            <Col xs={24} sm={24} md={8} lg={6} xl={6}>
                <Card style={{ marginBottom: '24px', border: 'none'}} >
                    <ProfileView />
                </Card>
            </Col>
            <Col xs={24} sm={24} md={16} lg={18} xl={18}>
                <Card style={{ marginBottom: '24px' }} title="Recent Entries">
                    <RecentEntriesView />
                </Card>
                <Card title="Recent Activities">
                    <ActivityHeatmap />
                </Card>
            </Col>
        </Row>
        </div>
    );
};

const Home: React.FC = () => {
    return (
        <MyLayout>
            <HomeContent />
        </MyLayout>
    );
};



export default Home;