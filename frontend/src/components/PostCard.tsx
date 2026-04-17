import React, { useMemo, useState } from "react";
import { Button, Card, Flex, Input, Select, Space, Tag, Typography, message } from "antd";
import { CheckCircleOutlined, DislikeOutlined, HeartOutlined, SaveOutlined } from "@ant-design/icons";

import { FeedbackResponse, PostResult, submitFeedback } from "../lib/mvpApi";

const { Paragraph, Text, Title } = Typography;

const feedbackOptions = [
  { label: "More personal", value: "more-personal" },
  { label: "Shorter", value: "shorter" },
  { label: "Less salesy", value: "less-salesy" },
  { label: "Warmer", value: "warmer" },
  { label: "More playful", value: "more-playful" },
  { label: "More reflective", value: "more-reflective" },
];

interface PostCardProps {
  post: PostResult;
  userId: string;
  onFeedbackApplied: (response: FeedbackResponse) => void;
}

const PostCard: React.FC<PostCardProps> = ({ post, userId, onFeedbackApplied }) => {
  const [draft, setDraft] = useState(post.content);
  const [tags, setTags] = useState<string[]>([]);
  const [submitting, setSubmitting] = useState(false);

  React.useEffect(() => {
    setDraft(post.content);
  }, [post.content]);

  const selectedLabel = useMemo(() => (post.is_selected ? "Selected voice" : "Candidate voice"), [post.is_selected]);

  const handleSendFeedback = async (signalType: "like" | "dislike" | "select" | "rewrite") => {
    setSubmitting(true);
    try {
      const response = await submitFeedback(post.post_id, {
        user_id: userId,
        signal_type: signalType,
        tags,
        rewrite_text: signalType === "rewrite" ? draft : "",
      });
      onFeedbackApplied(response);
      message.success(`Saved ${signalType} feedback for ${post.style_name}.`);
    } catch (error) {
      message.error(`Couldn't save ${signalType} feedback right now.`);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Card className="post-card" bordered={false}>
      <Flex align="center" justify="space-between">
        <div>
          <Text className="eyebrow">{selectedLabel}</Text>
          <Title level={4} className="post-style-title">
            {post.style_name}
          </Title>
        </div>
        {post.is_selected ? <Tag color="gold">Active preference</Tag> : <Tag>Draft</Tag>}
      </Flex>
      <Paragraph className="post-hook">{post.hook}</Paragraph>
      <Input.TextArea
        value={draft}
        onChange={(event) => setDraft(event.target.value)}
        autoSize={{ minRows: 7, maxRows: 14 }}
        className="post-editor"
      />
      <Space direction="vertical" size={12} className="full-width">
        <Select
          mode="multiple"
          allowClear
          placeholder="Label how this draft should improve"
          options={feedbackOptions}
          value={tags}
          onChange={(values) => setTags(values)}
        />
        <Flex gap={8} wrap="wrap">
          <Button icon={<HeartOutlined />} loading={submitting} onClick={() => handleSendFeedback("like")}>
            Like
          </Button>
          <Button icon={<DislikeOutlined />} loading={submitting} onClick={() => handleSendFeedback("dislike")}>
            Not Me
          </Button>
          <Button
            type="primary"
            icon={<CheckCircleOutlined />}
            loading={submitting}
            onClick={() => handleSendFeedback("select")}
          >
            Use This Style
          </Button>
          <Button icon={<SaveOutlined />} loading={submitting} onClick={() => handleSendFeedback("rewrite")}>
            Save Rewrite Signal
          </Button>
        </Flex>
      </Space>
    </Card>
  );
};

export default PostCard;
