import React, { useEffect, useState } from "react";
import { Card, Col, Empty, Flex, Row, Skeleton, Space, Statistic, Tag, Timeline, Typography, message } from "antd";

import { GrowthResponse, fetchGrowth } from "../lib/mvpApi";

const { Paragraph, Text, Title } = Typography;

interface GrowthPageProps {
  userId: string;
  refreshKey: number;
}

const GrowthPage: React.FC<GrowthPageProps> = ({ userId, refreshKey }) => {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<GrowthResponse | null>(null);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      try {
        const response = await fetchGrowth(userId);
        setData(response);
      } catch (error) {
        message.error("Couldn't load growth memory right now.");
      } finally {
        setLoading(false);
      }
    };

    void load();
  }, [userId, refreshKey]);

  if (loading) {
    return <Skeleton active paragraph={{ rows: 10 }} />;
  }

  if (!data) {
    return <Empty description="No growth data yet." />;
  }

  return (
    <Space direction="vertical" size={24} className="full-width">
      <section className="hero-panel">
        <div>
          <Text className="eyebrow">Growth memory + RAG</Text>
          <Title className="hero-title">Track how the user's voice, emotions, and recurring themes evolve over time.</Title>
          <Paragraph className="hero-copy">
            This page visualizes the long-term memory that feeds retrieval, style adaptation, and the sense of a continuing
            personal narrative.
          </Paragraph>
        </div>
      </section>

      <Row gutter={[16, 16]}>
        <Col xs={24} md={12} xl={6}>
          <Card className="soft-card stat-card" bordered={false}>
            <Statistic title="Collections" value={data.stats.collection_count} />
          </Card>
        </Col>
        <Col xs={24} md={12} xl={6}>
          <Card className="soft-card stat-card" bordered={false}>
            <Statistic title="Memories" value={data.stats.memory_count} />
          </Card>
        </Col>
        <Col xs={24} md={12} xl={6}>
          <Card className="soft-card stat-card" bordered={false}>
            <Statistic title="Feedback events" value={data.stats.feedback_count} />
          </Card>
        </Col>
        <Col xs={24} md={12} xl={6}>
          <Card className="soft-card stat-card" bordered={false}>
            <Statistic title="Top emotion" value={data.stats.top_emotion} />
          </Card>
        </Col>
      </Row>

      <Row gutter={[20, 20]}>
        <Col xs={24} xl={8}>
          <Card className="soft-card" bordered={false}>
            <Text className="eyebrow">Adaptive profile</Text>
            <Title level={3}>Current prompt memory</Title>
            <Paragraph>{data.profile.summary}</Paragraph>
            <Flex gap={8} wrap="wrap" className="tag-row">
              {data.profile.top_styles.map((style) => (
                <Tag color="gold" key={style}>
                  {style}
                </Tag>
              ))}
              {data.profile.top_tags.map((tag) => (
                <Tag key={tag}>{tag}</Tag>
              ))}
            </Flex>
            <Space direction="vertical" size={8} className="full-width">
              {data.profile.voice_notes.map((note) => (
                <div key={note} className="memory-item compact">
                  <Text>{note}</Text>
                </div>
              ))}
            </Space>
          </Card>
        </Col>

        <Col xs={24} xl={16}>
          <Card className="soft-card" bordered={false}>
            <Text className="eyebrow">Timeline</Text>
            {data.timeline.length ? (
              <Timeline
                items={data.timeline.map((memory) => ({
                  color: memory.source_type === "feedback" ? "#996c2f" : "#1f3c37",
                  children: (
                    <div className="timeline-entry">
                      <Text className="timeline-date">{new Date(memory.created_at).toLocaleString()}</Text>
                      <Title level={5}>{memory.title}</Title>
                      <Paragraph>{memory.summary}</Paragraph>
                      <Flex gap={8} wrap="wrap">
                        <Tag>{memory.emotion}</Tag>
                        <Tag color="green">{memory.growth_signal}</Tag>
                        {memory.keywords.map((keyword) => (
                          <Tag key={keyword}>{keyword}</Tag>
                        ))}
                      </Flex>
                    </div>
                  ),
                }))}
              />
            ) : (
              <Empty description="Timeline will populate after the first generation." />
            )}
          </Card>
        </Col>
      </Row>

      <Card className="soft-card" bordered={false}>
        <Text className="eyebrow">Recent collections</Text>
        <Row gutter={[16, 16]}>
          {data.collections.map((collection) => (
            <Col xs={24} md={12} xl={8} key={collection.collection_id}>
              <div className="collection-card">
                <Text className="timeline-date">{new Date(collection.created_at).toLocaleDateString()}</Text>
                <Title level={5}>{collection.title}</Title>
                <Paragraph>{collection.story_summary}</Paragraph>
                <Tag color="blue">{collection.emotional_tone}</Tag>
              </div>
            </Col>
          ))}
        </Row>
      </Card>
    </Space>
  );
};

export default GrowthPage;
