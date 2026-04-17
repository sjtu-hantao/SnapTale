import React from 'react';
import { Modal, Upload, message } from 'antd';
import { InboxOutlined } from '@ant-design/icons';
import type { UploadProps } from 'antd';
import axios from 'axios';

const { Dragger } = Upload;

interface UploadModalProps {
  isVisible: boolean;
  onClose: () => void;
  onUploadSuccess: (imageUrl: string) => void;
}

const UploadModal: React.FC<UploadModalProps> = ({ isVisible, onClose, onUploadSuccess }) => {

  const customRequest = async ({ file, onSuccess, onError }: any) => {
    const formData = new FormData();

    const photo_create = {
        device_id: window.device_id,
        location: 'home',
        file_name: file.name,
        file_type: file.type,
        file_size: file.size,
    }

    formData.append('photo_create', JSON.stringify(photo_create));
    formData.append('image', file);



    try {
      const response = await axios.post(`${window.backend_url}/users/${window.user_id}/photos`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      console.log('response:', response);
      if (response.status === 200) {
        onSuccess(response.data);
        message.success(`${file.name} uploaded successfully.`);
        onUploadSuccess(response.data.url);
      } else {
        onError(new Error('Upload failed'));
        message.error(`${file.name} upload failed.`);
      }
    } catch (error) {
      onError(error);
      message.error(`${file.name} upload failed.`);
    }
  };

  const props: UploadProps = {
    name: 'file',
    multiple: false,
    customRequest,
    beforeUpload: (file) => {
        const isImage = file.type.startsWith('image/');
        if (!isImage) {
          message.error(`${file.name} is not a valid image file`);
        }
        return isImage || Upload.LIST_IGNORE;
      },
    onChange(info) {
      const { status } = info.file;
      if (status !== 'uploading') {
        console.log(info.file, info.fileList);
      }
    },
    onDrop(e) {
      console.log('Dropped files', e.dataTransfer.files);
    },
  };

  return (
    <Modal title="Upload Photo" open={isVisible} onCancel={onClose} footer={null}>
      <Dragger {...props}>
        <p className="ant-upload-drag-icon">
          <InboxOutlined />
        </p>
        <p className="ant-upload-text">Click or drag image file to upload</p>
        <p className="ant-upload-hint">
            Support single upload only. Strictly prohibit uploading company data or other sensitive files.
        </p>
      </Dragger>
    </Modal>
  );
};

export default UploadModal;