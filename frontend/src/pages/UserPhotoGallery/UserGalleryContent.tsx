import React from 'react';
import { List, Image, Tooltip, Skeleton, Divider } from 'antd';
import InfiniteScroll from 'react-infinite-scroll-component';
import { PhotoResponse } from '../../utils/photos';
import { CheckCard } from '@ant-design/pro-components';

interface UserPhotoGalleryContentProps {
    loading: boolean;
    items: PhotoResponse[];
    onLoadMore: () => void;
    hasMore: boolean;
    handleCheck: (checked: boolean, photo_id: string) => void;
}

const UserPhotoGalleryContent: React.FC<UserPhotoGalleryContentProps> = React.memo(
    ({ loading, items, onLoadMore, hasMore, handleCheck }) => {
        const isMobile = window.innerWidth < 768; // 判断是否是小屏幕设备

        return (
            <InfiniteScroll
                dataLength={items.length}
                next={onLoadMore}
                hasMore={hasMore}
                loader={<Skeleton paragraph={{ rows: 1 }} active />}
                endMessage={<Divider plain>It is all, nothing more 🤐</Divider>}
            >
                <List
                    grid={{
                        gutter: 8, // 适当增加列之间的间距
                        xs: 1, // 小屏幕下每行显示2列
                        sm: 2,
                        md: 4,
                        lg: 4,
                        xl: 6,
                        xxl: 8,
                    }}
                    size='large'
                    dataSource={items}
                    renderItem={(item) => {
                        return (
                            <List.Item>
                                <CheckCard
                                    title={item.time_created}
                                    description={null}
                                    value={item.photo_id}
                                    style={{
                                        width: isMobile ? '60vw' : '200px', // 移动端宽度更小
                                        height: 'auto',
                                        display: 'flex',
                                        flexDirection: 'column',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                        textAlign: 'center',
                                        margin: '0 auto', // 让卡片在列表中居中显示
                                    }}
                                    onChange={(checked) => {
                                        handleCheck(checked, item.photo_id);
                                    }}
                                >
                                    <Tooltip title={item.description}>
                                        <Image
                                            style={{
                                                width: '100%',
                                                height: isMobile ? 'auto' : '20vh', // 小屏幕高度较小
                                                objectFit: 'cover',
                                                display: 'block',
                                                margin: '0 auto',
                                            }}
                                            src={`${item.url}`}
                                        />
                                    </Tooltip>
                                </CheckCard>
                            </List.Item>
                        );
                    }}
                />
            </InfiniteScroll>
        );
    }
);

export default UserPhotoGalleryContent;
