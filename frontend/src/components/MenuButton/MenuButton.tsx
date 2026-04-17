import React from "react";
import { FloatButton } from "antd";
import {
  HomeOutlined,
  SettingOutlined,
  PlusOutlined,
  BookOutlined,
  PictureOutlined,
  MenuOutlined,
} from "@ant-design/icons";
import { addUserJournal } from "../../utils/journals";

const MenuButton: React.FC = () => {
  return (
    <FloatButton.Group
      trigger="hover"
      type="primary"
      style={{ right: 24 }}
      icon={<MenuOutlined/>}
    >
      <FloatButton
        icon={<HomeOutlined />}
        tooltip="Home"
        onClick={() => {
            console.log("Navigating to Home");
            window.location.href = "/";
        }}
      />
      <FloatButton
        icon={<SettingOutlined />}
        tooltip="Settings"
        onClick={() => console.log("Navigating to Settings")}
      />
      <FloatButton
        icon={<PictureOutlined />}
        tooltip="Gallery View"
        onClick={() => {
          console.log("Navigating to Gallery View");
          window.location.href = "/gallery";
      }}
      />
      <FloatButton
        icon={<BookOutlined />}
        tooltip="Journal List View"
        onClick={() => {
            console.log("Navigating to Journal List View");
            window.location.href = "/journals";
        }}
      />
      <FloatButton
        icon={<PlusOutlined />}
        tooltip="New Journal"
        onClick={() => {
          console.log("Navigating to New Journal");
          addUserJournal(window.user_id)
          .then((journal) => {
            console.log("Navigating to Journal:", journal.id);
            window.location.href = `/journalview?journalId=${journal.journal_id}`;
          })
          .catch((error) => {
            console.error("Error adding user journal:", error);
          });
    }}
      />
    </FloatButton.Group>
  );
};

export default MenuButton;
