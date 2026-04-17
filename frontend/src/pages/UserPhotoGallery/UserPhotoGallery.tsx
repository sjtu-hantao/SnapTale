import React, { useEffect, useCallback, useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import MyLayout from '../../components/Layout';
import SearchBar, { SearchFilters } from '../../components/SearchBar/SearchBar';
import { Space, FloatButton, message } from 'antd';
import getUserPhoto, { PhotoResponse } from '../../utils/photos';
import GalleryButtons from './GalleryButton';
import UserPhotoGalleryContent from './UserGalleryContent';
import { deleteUserPhotos, describeUserPhoto, downloadSelectedPhotos, generateJournalFromPhotos } from '../../utils/photos';

function calculateLimit() {
    const screenWidth = window.innerWidth;
    const screenHeight = window.innerHeight;

    // 修改图片和间距的大小以适应不同的屏幕尺寸
    const imageWidth = screenWidth < 768 ? 100 : 150; // 如果屏幕宽度小于768px，使用较小的图片宽度
    const imageHeight = screenWidth < 768 ? 200 : 300; // 适应图片高度
    const horizontalGap = screenWidth < 768 ? 5 : 10; // 更小的间距在小屏幕上
    const verticalGap = screenWidth < 768 ? 5 : 10;

    const columns = Math.floor(screenWidth / (imageWidth + horizontalGap));
    const rows = Math.floor(screenHeight / (imageHeight + verticalGap));
    const limit = columns * rows;

    return limit;
}

const UserPhotoGallery: React.FC = () => {
    const [filter, setFilter] = useState<SearchFilters>({
        starred: false,
        device: null,
        fromDate: null,
        toDate: null,
        contains: null,
    });
    const [loading, setLoading] = useState<boolean>(false);
    const [photoData, setPhotoData] = useState<PhotoResponse[]>([]);
    const [hasMore, setHasMore] = useState<boolean>(true);
    const [checkPhoto, setCheckPhoto] = useState<string[]>([]);
    const userId = window.user_id;
    const limit = calculateLimit();
    const navigate = useNavigate();
    const isInitialMount = useRef(true);

    const fetchPhotos = useCallback(async (isInitialFetch: boolean = false) => {
        if (isInitialMount.current) {
            isInitialMount.current = false;
            return;
        }
        if (loading) return;
        setLoading(true);
        try {
            const offset = isInitialFetch ? 0 : photoData.length;
            const data = await getUserPhoto(userId, filter, offset, limit);
            setPhotoData(prevData => isInitialFetch ? data : [...prevData, ...data]);
            setHasMore(data.length === limit);
        } catch (error) {
            console.error('Error fetching user photo:', error);
            message.error('Failed to fetch photos. Please try again.');
        } finally {
            setLoading(false);
        }
    }, [filter, photoData.length, loading]);

    useEffect(() => {
        fetchPhotos(true);
    }, [filter]);

    const handleFilterChange = (newFilter: SearchFilters) => {
        setFilter(newFilter);
        const params = new URLSearchParams();
        if (newFilter?.starred) params.set('starred', 'true');
        else params.delete('starred');
        if (newFilter?.device) params.set('device', newFilter?.device);
        if (newFilter?.fromDate) params.set('fromDate', newFilter?.fromDate);
        if (newFilter?.toDate) params.set('toDate', newFilter?.toDate);
        if (newFilter?.contains) params.set('contains', newFilter?.contains);

        navigate({ search: params.toString() });
    }

    const handleLoadMore = () => {
        fetchPhotos();
    };

    const handleCheck = (checked: boolean, photo_id: string) => {
        setCheckPhoto(prevData => checked ? [...prevData, photo_id] : prevData.filter(id => id !== photo_id));
    };

    const handleEdit = async () => {
        message.info('Describing photos...');
        if (checkPhoto.length === 0) {
            message.error('Please select photos to describe.');
            return;
        }
        const data = await describeUserPhoto(userId, checkPhoto[0]);
        console.log('Described photo:', data);
        setPhotoData(prevData => prevData.map(item => item.photo_id === checkPhoto[0] ? data : item));
        message.success('Photos described successfully.');
    };

    const handleDownload = async () => {
        const photoUrls = checkPhoto.map(photoId => photoData.find(item => item.photo_id === photoId)?.url).filter(url => url !== undefined) as string[];

        message.info('Downloading photos...');
        if (photoUrls.length === 0) {
            message.error('Please select photos to download.');
            return;
        }

        try {
            const zipBlob = await downloadSelectedPhotos(userId, photoUrls);

            // Create a temporary URL for the ZIP blob
            const blobUrl = URL.createObjectURL(zipBlob);

            // Create a link element and trigger download
            const link = document.createElement('a');
            link.href = blobUrl;
            link.download = 'selected_photos.zip';
            link.click();

            // Clean up the temporary URL
            URL.revokeObjectURL(blobUrl);

            message.success('Photos downloaded successfully!');

        } catch (error) {
            console.error('Error downloading photos:', error);
            message.error('Failed to download photos. Please try again.');
        }
    };

    const handleDelete = async () => {
        message.info('Deleting photos...');
        if (checkPhoto.length === 0) {
            message.error('Please select photos to delete.');
            return;
        }
        try {
            await deleteUserPhotos(userId, checkPhoto);
            message.success('Photos deleted successfully.');
            setCheckPhoto([]);
            fetchPhotos(true);
        } catch (error) {
            console.error('Error deleting photos:', error);
            message.error('Failed to delete photos. Please try again.');
        };
    };

    const handleGenerate = async () => {
        if (checkPhoto.length === 0) {
            message.error('Please select photos to generate journal.');
            return;
        }
        message.info('Generating journal...');
        try {
            await generateJournalFromPhotos(userId, checkPhoto);
            // Redirect to journal page upon confirm
            if (window.confirm('Journal generated successfully. Click OK to redirect to another page.')) {
            window.location.href = '/journals';
            } 
        } catch (error) {
            console.error('Error generating journal:', error);
            message.error('Failed to generate journal. Please try again.');
        }
    };

    useEffect(() => {
        console.log('Updated checkPhoto:', checkPhoto);
        console.log('Updated filter:', filter);
    }, [checkPhoto, filter]);

    return (
        <MyLayout>
            <Space direction="vertical" size="large">
                <SearchBar onFilterChange={handleFilterChange} initFilters={filter} />
                <GalleryButtons
                    checkPhotoNum={checkPhoto.length}
                    handleDelete={handleDelete}
                    handleEdit={handleEdit}
                    handleDownload={handleDownload}
                    handleGenerate={handleGenerate}
                />
                <UserPhotoGalleryContent
                    loading={loading}
                    items={photoData}
                    onLoadMore={handleLoadMore}
                    hasMore={hasMore}
                    handleCheck={handleCheck}
                />
                <FloatButton.BackTop style={{ right: 94, }} />
            </Space>
        </MyLayout>
    );
};


export default UserPhotoGallery;
