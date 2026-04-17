import React from 'react';
import { useState } from 'react';
import { Button, Space } from 'antd';
import { DeleteOutlined, FileAddOutlined, DownloadOutlined } from '@ant-design/icons';
import UploadModal from "../../components/UploadModal/UploadModel";
import { PiShootingStarFill } from "react-icons/pi";
import { BsStars } from "react-icons/bs";


interface GalleryButtonsProps {
    checkPhotoNum?: number;
    handleDelete?: () => void;
    handleEdit?: () => void;
    handleDownload?: () => void;
    handleGenerate?: () => void;
    onUploadSuccess?: (imageUrl: string) => void;
}
const GalleryButtons: React.FC<GalleryButtonsProps> = ({checkPhotoNum, handleDownload, handleDelete, handleEdit, handleGenerate, onUploadSuccess }) => {
    const [isUploadModalVisible, setIsUploadModalVisible] = useState(false);

    const handleAdd = () => {
        setIsUploadModalVisible(true);
    }

    const handleCloseUploadModal = () => {
        setIsUploadModalVisible(false);
        window.location.reload();

    };

    return (
      
        <Space align="center" style={{ justifyContent: 'left', width: '80vw' }} wrap>
        <Button type="primary" shape="round" icon={<DeleteOutlined />} size={'middle'} onClick={handleDelete} disabled={(checkPhotoNum !== undefined && checkPhotoNum === 0) || false}>
          Delete
        </Button>
        <Button type="primary" shape="round" icon={<FileAddOutlined />} size={'middle'} onClick={handleAdd}>
          Add
        </Button>
        <Button type="primary" shape="round" icon={<BsStars />} size={'middle'} onClick={handleEdit} disabled={(checkPhotoNum !== undefined && (checkPhotoNum > 1 || checkPhotoNum === 0)) || false}>
          Describe
        </Button>
        <Button type="primary" shape="round" icon={<DownloadOutlined />} size={'middle'} onClick={handleDownload} disabled={(checkPhotoNum !== undefined && checkPhotoNum === 0) || false}>
          Download
        </Button>
        <Button type="primary" shape="round" icon={<PiShootingStarFill /> } size={'middle'} className="gradient-button" onClick={handleGenerate} disabled={(checkPhotoNum !== undefined && checkPhotoNum === 0) || false}> 
          Generate Journal
        </Button>
        <UploadModal
                isVisible={isUploadModalVisible}
                onClose={handleCloseUploadModal}
                onUploadSuccess={onUploadSuccess? onUploadSuccess : () => {}}
            />
        </Space>
    )


}

export default GalleryButtons;
