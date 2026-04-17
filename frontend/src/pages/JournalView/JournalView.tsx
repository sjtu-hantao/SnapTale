import React, { useState, useEffect, useRef } from 'react';
import MyLayout from '../../components/Layout';
import { Button, message, Tooltip } from 'antd';
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm';
import MarkdownEditor from 'react-markdown-editor-lite';
import 'react-markdown-editor-lite/lib/index.css';
import handleJournalDetails, {handleJournalUpdate} from '../../utils/getJournal';
import { BrowserRouter as Router, Route, useLocation } from 'react-router-dom';

import './JournalView.css';


interface JournalViewContentProps {
  journalContent: string | undefined;
  handleJournalChange?: (journalContent: string | undefined) => void;
}

const JournalViewContent: React.FC<JournalViewContentProps> = ({ journalContent, handleJournalChange }) => {
    const [markdown, setMarkdown] = useState<string| undefined >(); // There must be no type/blank at the beginning of lines
    console.log('Journal content:', journalContent);
    const currentUrl = window.location.href; // 获取当前地址栏的全部内容
    useEffect(() => {
        setMarkdown(journalContent);
    }, [journalContent]);

    const [isEditing, setIsEditing] = useState(false);
        
    const handleEditorChange = ({ text }: { text: string }) => {
        setMarkdown(text);
        // Send the markdown to the server
    };

    const toggleEditMode = () => {
        setIsEditing(!isEditing);
        if (isEditing) {
            handleJournalChange && handleJournalChange(markdown);
        }
    };

    return (
        <div className="app-container">
            
            {isEditing ? (

            <MarkdownEditor
                value={markdown}
                style={{ height: '70vh', width: '100%' }}
                renderHTML={text => <ReactMarkdown 
                    remarkPlugins={[remarkGfm]}
                    components={{
                        img: ({ node, ...props }) => ( 
                            <img 
                            alt=''
                            style={{ 
                                maxWidth: '40vw',
                                maxHeight: '40vh',
                                display: 'block',
                                margin: '5px auto',}} {...props} />

                            
                        ),
                    }}>
                    {text}
                    </ReactMarkdown>}
                
                onChange={handleEditorChange}
            />

            ) : (
                <div className="markdown-preview">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}
                    components={{
                        img: ({ node, ...props }) => ( 
                            <img alt='' style={{ 
                                maxWidth: '40vw',
                                maxHeight: '40vh',
                                display: 'block',
                                margin: '10px auto',
                                }} {...props} />
                            
                        ),
                    }}>
                        {markdown}
                    </ReactMarkdown>
                </div>
            )}
            <div className="button-container">
        <Button onClick={toggleEditMode} style={{ marginBottom: '20px' }}>
            {isEditing ? 'Save' : 'Edit'}
        </Button>

        <Tooltip title={currentUrl}>
        <Button style={{ marginBottom: '20px', marginLeft: '10px' }}>
            Forward
        </Button>
        </Tooltip>

        
        </div>
        </div>
    );
}


const JournalView: React.FC = () => {
    // Acquire the journal id from the URL
    // Fetch the journal content from the server

    const location = useLocation();

    // 使用useLocation钩子获取当前URL
    const params = new URLSearchParams(location.search);
    // 读取fromDate和toDate参数
    const journalId = params.get('journalId') || '';

    const [journalContent, setJournalContent] = useState<string | undefined>('');
    const isInitialMount = useRef(true);

    useEffect(() => {
        if(isInitialMount.current) {
            isInitialMount.current = false;
            return;
        }
        console.log('Fetching journal content for journal id:', journalId);
        handleJournalDetails({ journalId }).then((data) => {

            setJournalContent(data);
        });
    }, []);

    const handleJournalChange = (updateContent: string | undefined) => {
        console.log('Updating journal content for journal id:', journalId);
        setJournalContent(updateContent);
        handleJournalUpdate({ journalId, journalContent: updateContent }).then((isSuccess) => {
            if (isSuccess) {
                message.success('Journal updated successfully');
            } else {
                message.error('Journal update failed');
        }
    });
    }

    return (
        <MyLayout>
            <JournalViewContent journalContent={journalContent} handleJournalChange={handleJournalChange}/>
        </MyLayout>
    );
};

export default JournalView;