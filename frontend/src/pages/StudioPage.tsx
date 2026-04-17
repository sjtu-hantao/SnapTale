import React, { useState } from "react";
import { Alert, Button, Card, Col, Empty, Flex, Form, Input, Row, Space, Tag, Typography, Upload, message } from "antd";
import type { UploadFile } from "antd/es/upload/interface";
import { InboxOutlined } from "@ant-design/icons";

import PostCard from "../components/PostCard";
import { FeedbackResponse, GenerateResponse, generateStoryboard } from "../lib/mvpApi";

const { Dragger } = Upload;
const { Paragraph, Text, Title } = Typography;

interface StudioPageProps {
  userId: string;
  onActivityChange: () => void;
}

const StudioPage: React.FC<StudioPageProps> = ({ userId, onActivityChange }) => {
  const [form] = Form.useForm();
  const [fileList, setFileList] = useState<UploadFile[]>([]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<GenerateResponse | null>(null);

  const handleGenerate = async () => {
    const values = await form.validateFields();
    const files = fileList.reduce<File[]>((accumulator, item) => {
      if (item.originFileObj) {
        accumulator.push(item.originFileObj as File);
      }
      return accumulator;
    }, []);

    if (!files.length) {
      message.error("Please upload at least one photo set.");
      return;
    }

    setLoading(true);
    try {
      const response = await generateStoryboard({
        userId,
        title: values.title,
        context: values.context,
        files,
      });
      setResult(response);
      onActivityChange();
      message.success("Story agent finished a first pass.");
    } catch (error) {
      message.error("Generation failed. Please verify the backend is running.");
    } finally {
      setLoading(false);
    }
  };

  const handleFeedbackApplied = (feedback: FeedbackResponse) => {
    setResult((current) =>
      current
        ? {
            ...current,
            posts: feedback.posts,
            profile: feedback.profile,
          }
        : current,
    );
    onActivityChange();
  };

  const renderGenerationStatus = () => {
    if (!result) {
      return null;
    }

    const info = result.generation_info;
    const primaryLine = info.use_llm
      ? `Model provider: ${info.provider}. Story generation: ${info.story_generation_mode}. Image analysis: ${info.image_analysis_mode} (${info.image_llm_used_count}/${info.image_total_count} via LLM).`
      : `Heuristic fallback mode is active. ${info.fallback_reason || "No model credentials were detected."}`;
    const secondaryLine = info.use_llm
      ? `Vision model: ${info.vision_model || "n/a"}. Text model: ${info.text_model || "n/a"}.`
      : "Add ARK_API_KEY and ARK model settings in backend/.env to enable real model generation.";
    const notes = info.provider_notes.length ? ` Notes: ${info.provider_notes.join(" ")}` : "";

    return (
      <Alert
        type={info.use_llm && info.story_generation_mode === "llm" ? "success" : "warning"}
        showIcon
        message={primaryLine}
        description={`${secondaryLine}${notes}`}
      />
    );
  };

  return (
    <Space direction="vertical" size={24} className="full-width">
      <section className="hero-panel">
        <div>
          <Text className="eyebrow">One-click social content</Text>
          <Title className="hero-title">Upload a photo set, get a story arc, platform-ready posts, and evolving voice memory.</Title>
          <Paragraph className="hero-copy">
            This MVP keeps the product focused on the three hardest things: multi-photo story inference, adaptive
            writing preferences, and a growth timeline built from long-term memory.
          </Paragraph>
        </div>
      </section>

      <Row gutter={[20, 20]}>
        <Col xs={24} xl={9}>
          <Card className="soft-card" bordered={false}>
            <Form form={form} layout="vertical" initialValues={{ title: "This Week's Chapter", context: "" }}>
              <Form.Item
                name="title"
                label="Collection title"
                rules={[{ required: true, message: "Give this moment a working title." }]}
              >
                <Input placeholder="Weekend reset, new habit, small celebration..." />
              </Form.Item>
              <Form.Item name="context" label="Optional context for the agent">
                <Input.TextArea
                  autoSize={{ minRows: 4, maxRows: 7 }}
                  placeholder="What was happening around these photos? Any emotion, people, or milestone we should preserve?"
                />
              </Form.Item>
              <Form.Item label="Photo set">
                <Dragger
                  multiple
                  fileList={fileList}
                  beforeUpload={() => false}
                  onChange={({ fileList: nextList }) => setFileList(nextList)}
                  accept="image/*"
                  className="upload-box"
                >
                  <p className="ant-upload-drag-icon">
                    <InboxOutlined />
                  </p>
                  <p className="ant-upload-text">Drop 2-8 photos to build one story collection</p>
                  <p className="ant-upload-hint">The agent will infer emotional tone, narrative arc, and social post variants.</p>
                </Dragger>
              </Form.Item>
              <Button type="primary" size="large" block loading={loading} onClick={handleGenerate}>
                Generate Story + Social Posts
              </Button>
            </Form>
          </Card>
        </Col>

        <Col xs={24} xl={15}>
          {result ? (
            <Space direction="vertical" size={20} className="full-width">
              <Card className="soft-card" bordered={false}>
                <Text className="eyebrow">Agent summary</Text>
                <Title level={3}>{result.collection.title}</Title>
                <Paragraph>{result.collection.story_summary}</Paragraph>
                <Alert
                  type="info"
                  showIcon
                  message={`Narrative arc: ${result.collection.narrative_arc}`}
                  description={`Emotional tone: ${result.collection.emotional_tone}. Current adaptive profile: ${result.profile.summary}`}
                />
                {renderGenerationStatus()}
                <Flex gap={8} wrap="wrap" className="tag-row">
                  {result.profile.top_styles.map((style) => (
                    <Tag key={style} color="gold">
                      {style}
                    </Tag>
                  ))}
                  {result.profile.top_tags.map((tag) => (
                    <Tag key={tag}>{tag}</Tag>
                  ))}
                </Flex>
              </Card>

              <Card className="soft-card" bordered={false}>
                <Text className="eyebrow">Retrieved memory</Text>
                {result.retrieved_memories.length ? (
                  <Space direction="vertical" size={12} className="full-width">
                    {result.retrieved_memories.map((memory) => (
                      <div key={memory.memory_id} className="memory-item">
                        <Text strong>{memory.title}</Text>
                        <Paragraph>{memory.summary}</Paragraph>
                      </div>
                    ))}
                  </Space>
                ) : (
                  <Paragraph>No previous memories yet. The first generation just seeded one.</Paragraph>
                )}
              </Card>

              <Card className="soft-card" bordered={false}>
                <Text className="eyebrow">Cross-modal evidence</Text>
                <Row gutter={[16, 16]}>
                  {result.assets.map((asset) => (
                    <Col xs={24} md={12} key={asset.asset_id}>
                      <div className="asset-card">
                        <img src={asset.public_url} alt={asset.file_name} className="asset-image" />
                        <div>
                          <Text strong>{asset.file_name}</Text>
                          <Paragraph className="asset-analysis">{asset.analysis_text}</Paragraph>
                          <Tag>{asset.mood_tag}</Tag>
                        </div>
                      </div>
                    </Col>
                  ))}
                </Row>
              </Card>

              <Row gutter={[16, 16]}>
                {result.posts.map((post) => (
                  <Col xs={24} lg={12} key={post.post_id}>
                    <PostCard post={post} userId={userId} onFeedbackApplied={handleFeedbackApplied} />
                  </Col>
                ))}
              </Row>
            </Space>
          ) : (
            <Card className="soft-card empty-panel" bordered={false}>
              <Empty
                description="Your first result set will appear here with story analysis, retrieved memories, and multiple post styles."
              />
            </Card>
          )}
        </Col>
      </Row>
    </Space>
  );
};

export default StudioPage;
