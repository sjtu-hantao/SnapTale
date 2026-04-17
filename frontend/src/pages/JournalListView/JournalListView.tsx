import React, { useEffect, useCallback, useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { BrowserRouter as Router, Route, useLocation } from 'react-router-dom';
import MyLayout from '../../components/Layout';
import SearchBar, { SearchFilters } from '../../components/SearchBar/SearchBar';
import { List, Tag, Skeleton, Divider, FloatButton, message } from 'antd';
import { DeleteOutlined, StarFilled, StarOutlined } from '@ant-design/icons';
import InfiniteScroll from 'react-infinite-scroll-component';
import getUserJournal, { deleteUserJournal, JournalResponse, toggleUserJournalStar} from '../../utils/journals';
import IconText from '../../components/IconText/IconText';
import { findFirstUrl } from '../Home/RecentEntriesView';
import dayjs from 'dayjs'

const dateFormat = 'YYYY-MM-DD HH:mm:ss';


const StyledStarOutlined = (props: React.SVGProps<SVGSVGElement>) => (
    <StarOutlined style={{ color: 'gray', ...props.style }} />
);

const StyledStarFilled = (props: React.SVGProps<SVGSVGElement>) => (
    <StarFilled style={{ color: '#FFD700', ...props.style }} />
);

interface JournalListContentProps {
    loading: boolean;
    items: JournalResponse[];
    onLoadMore: () => void;
    hasMore: boolean;
}

const JournalListContent: React.FC<JournalListContentProps> = React.memo(
    ({ loading, items, onLoadMore, hasMore }) => {

        const toggleStar = (item: any) => {
    
            console.log('starred:', item.journal_id, item.starred);
            
            try{
                toggleUserJournalStar(window.user_id, item.journal_id, item.starred);
            }
            catch (error) {
                console.error('Error toggling star:', error);
                message.error('Failed to toggle star. Please try again.');
            }
        };

        const deleteJournal = (item: any) => {
            console.log('delete:', item.journal_id);
            try{
                // deleteJournal(window.user_id, item.journal_id);
                const isConfirmed = window.confirm('Are you sure you want to delete this journal?');
                if (isConfirmed) {
                    // Perform the action if confirmed
                    console.log('Journal deleted.');
                    // Replace the above line with your deletion logic, e.g., API call
                    deleteUserJournal(window.user_id, item.journal_id);
                    window.location.reload();
                } else {
                    // Action if cancelled
                    console.log('Deletion cancelled.');
                }
            }
            catch (error) {
                console.error('Error deleting journal:', error);
                message.error('Failed to delete journal. Please try again.');
            }
        }

        return (
            <InfiniteScroll
                dataLength={items.length}
                next={onLoadMore}
                hasMore={hasMore}
                loader={<Skeleton paragraph={{ rows: 1 }} active />}
                endMessage={<Divider plain>It is all, nothing more 🤐</Divider>}
            >
                <List
                    itemLayout="vertical"
                    size="large"
                    dataSource={items}
                    renderItem={(item) => (
                        <List.Item
                            key={item.journal_id}
                            actions={[
                                <IconText iconOff={StyledStarOutlined} iconOn={StyledStarFilled} text={item.datetime} key="list-vertical-star-o" defaultValue={item.starred} onClick={() => toggleStar(item)}/>,
                                <IconText iconOff={DeleteOutlined} iconOn={DeleteOutlined} text={item.datetime} key="list-vertical-star-o" defaultValue={item.starred} onClick={() =>deleteJournal(item)}/>,
                                <span>{dayjs(item.time_modified).format(dateFormat)}</span>,
                                ...(item.tags?.map((tag, index) => (
                                    <Tag color="blue" key={index}>
                                        {tag}
                                    </Tag>
                                )) ?? []),
                            ]}
                            extra={
                                <div style={{ overflow: 'hidden' }}>
                                    <img
                                        width={200}
                                        alt="logo"
                                        src={item.cover || "https://gw.alipayobjects.com/zos/rmsportal/JiqGstEfoWAOHiTxclqi.png"}
                                    />
                                </div>
                            }
                        >
                            <List.Item.Meta
                                title={<a href={`/journalview?journalId=${item.journal_id}`}>{item.title}</a>}
                                description={item.description}
                            />
                            {item.content}
                        </List.Item>
                    )}
                />
            </InfiniteScroll>
        );
    }
);


// FIXME: this is working but got some error: Unchecked runtime.lastError: A listener indicated an asynchronous response by returning true, but the message channel closed before a response was received
const JournalListView: React.FC = () => {

    const location = useLocation();

    // 使用useLocation钩子获取当前URL
    const queryParams = new URLSearchParams(location.search);
    // 读取fromDate和toDate参数
    const fromDate = queryParams.get('fromDate');
    const toDate = queryParams.get('toDate');
    const starred = queryParams.get('starred');
    const device = queryParams.get('device');
    const contains = queryParams.get('contains');
  

    const [filter, setFilter] = useState<SearchFilters>({
        starred: starred === 'true',
        device: device,
        fromDate: fromDate,
        toDate: toDate,
        contains: contains,
    });
    const [loading, setLoading] = useState<boolean>(false);
    const [journalData, setJournalData] = useState<JournalResponse[]>([]);
    const [hasMore, setHasMore] = useState<boolean>(true);
    const isInitialMount = useRef(true);
    const userId = window.user_id;
    const limit = 10;

    const navigate = useNavigate();

    const fetchJournals = useCallback(async (isInitialFetch: boolean = false) => {
        if (isInitialMount.current) {
            isInitialMount.current = false;
            return;
        }
        if (loading) return;
        setLoading(true);
        try {
            const offset = isInitialFetch ? 0 : journalData.length;
            const data = await getUserJournal(userId, filter, offset, limit);
            // Get the cover url
            if (data) {
                for (let entry of data) {
                    const url = findFirstUrl(entry.description ? entry.description : '');
                    if (url) {
                      entry.cover = url;
                    }
                  }
            }

            setJournalData(prevData => isInitialFetch ? data : [...prevData, ...data]);
            console.log('journalData:', journalData);
            setHasMore(data.length === limit);
        } catch (error) {
            console.error('Error fetching user journal:', error);
            message.error('Failed to fetch journals. Please try again.');
        } finally {
            setLoading(false);
        }
    }, [filter, journalData.length, loading]);

    useEffect(() => {
        fetchJournals(true);
        
    }, [filter]);

    const handleFilterChange = (newFilter: SearchFilters) => {
        setFilter(newFilter);
        // Perform actions based on updated filters
        const params = new URLSearchParams();
        if (newFilter?.starred) params.set('starred', 'true');
            else params.delete('starred');
        if (newFilter?.device) params.set('device', newFilter?.device);
        if (newFilter?.fromDate) params.set('fromDate', newFilter?.fromDate);
        if (newFilter?.toDate) params.set('toDate', newFilter?.toDate);
        if (newFilter?.contains) params.set('contains', newFilter?.contains);

        navigate({ search: params.toString() });
    };

    const handleLoadMore = () => {
        fetchJournals();
    };

    console.log('journalData:', filter);

    return (
        <MyLayout>
            <SearchBar onFilterChange={handleFilterChange} initFilters={filter}/>
            <JournalListContent
                loading={loading}
                items={journalData}
                onLoadMore={handleLoadMore}
                hasMore={hasMore}
            />
            <FloatButton.BackTop style={{ right: 94 }} />
        </MyLayout>
    );
};

export default JournalListView;