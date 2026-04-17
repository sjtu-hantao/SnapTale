import React, { useEffect, useRef } from 'react';
import { List, Card, message } from 'antd';
import axios from 'axios';
import dayjs from 'dayjs';

export interface Entry {
    journal_id: string;
    time_modified: string;
    description?: string;
    title?: string;
    cover?: string | null;
    tags?: string[];
    url?: string;
}

export function findFirstUrl(markdown: string): string | null {
    // The regex to match the URL
    const urlPattern = /https?:\/\/[^\s)]+/g;
    const match = urlPattern.exec(markdown);
    
    // Return the first match
    return match ? match[0] : null;
}

const RecentEntriesView: React.FC = () => {
    const dateFormat = 'YYYY-MM-DD HH:mm:ss';
    const [entries, setEntries] = React.useState<Entry[]>();
    const isInitialMount = useRef(true);

    useEffect(() => {
        if (isInitialMount.current) {
            isInitialMount.current = false;
            return;
        }
        message.loading({ content: 'Loading recent entries...', key: 'entries', duration: 0 });
        axios.get(window.backend_url + '/users/' + window.user_id + '/journals?limit=4&sortby=time_modified&order=desc')
            .then((response) => {
                console.log(response.data);
                for (let entry of response.data) {
                    const url = findFirstUrl(entry.description ? entry.description : '');
                    if (url) {
                        entry.cover = url;
                    }
                }
                console.log("response", response.data);

                setEntries(response.data);
                message.destroy('entries');
            })
            .catch((error) => {
                console.log(error);
            });
        // fetch entries from backend

    }, []);

    return (
        <div style={{ overflowX: 'auto', display: 'flex', padding: '10px 0' }}>
            {entries && entries.map((Item) => (
                <div style={{ width: '250px', marginRight: '16px', flexShrink: 0 }} key={Item.journal_id}>
                    <a href={`/journalview?journalId=${Item.journal_id}`}>
                        <Card
                            hoverable
                            cover={
                                <img
                                    src={Item.cover || "https://gw.alipayobjects.com/zos/rmsportal/JiqGstEfoWAOHiTxclqi.png"}
                                    style={{
                                        width: '100%',
                                        height: '20vh',
                                        objectFit: 'cover', // 保持图片比例并填充整个区域
                                        display: 'block' // 确保图片在块级显示
                                    }}
                                    alt={Item.url}
                                />
                            }
                        >
                            <Card.Meta title={Item.title} description={dayjs(Item.time_modified).format(dateFormat)} />
                        </Card>
                    </a>
                </div>
            ))}
        </div>
    );
}

export default RecentEntriesView;
