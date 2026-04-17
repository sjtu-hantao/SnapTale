import React, { useEffect, useState, useRef } from 'react';
import { Divider, Image, message, Space } from 'antd';
import Title from 'antd/es/typography/Title';
import axios from 'axios';

const SampleUserData = {
    "username": "octocate",
    "profile_picture_url": "https://via.placeholder.com/200",
    "email": "dfafaafaf@sjdaa.com",
    "bio": "This user hasn't written anything about themselves yet.",
    "time_created" : "2021-09-01"
}

const ProfileView: React.FC = () => {
    const [userData, setUserData] = useState(SampleUserData);
    const isInitialMount = useRef(true);

    useEffect(() => {
        if (isInitialMount.current) {
            isInitialMount.current = false;
            return;
        }
        message.loading({ content: 'Loading...', key: 'profile', duration: 0 });
        axios.get(window.backend_url + '/users/' + window.user_id)
            .then((response) => {
                const date = new Date(response.data.time_created);
                response.data.time_created = `${date.getFullYear()}-${date.getMonth() + 1}-${date.getDate()}`;
                response.data.profile_picture_url = response.data.profile_picture_url || SampleUserData.profile_picture_url;
                response.data.bio = response.data.bio || SampleUserData.bio;
                setUserData(response.data);
                message.destroy('profile');
            })
            .catch((error) => {
                console.log(error);
            });
    }, []);

    return (
        <Space 
            direction="vertical" 
            align="center" 
            style={{ width: '100%', maxWidth: '600px', margin: '0 auto', padding: '16px', textAlign: 'center' }}
        >
            <Image 
                src={userData.profile_picture_url} 
                alt="Profile picture" 
                style={{ borderRadius: '50%', width: '100%', maxWidth: '200px' }} 
                preview={false} 
            />
            <Title level={2} style={{ fontSize: '1.5rem', wordWrap: 'break-word', maxWidth: '100%' }}>
                {userData.username}
            </Title>
            <span  style={{ fontSize: '1rem', maxWidth: '100%',  wordWrap: 'break-word' }}>{userData.bio}<br></br></span>
            <a href={`mailto:${userData.email}`} style={{ fontSize: '0.9rem', wordWrap: 'break-word', maxWidth: '100%', color:'gray'}}>{userData.email}</a>
            <div style={{ fontSize: '0.9rem', wordWrap: 'break-word', maxWidth: '100%' , color:'gray'}}>Joined on {userData.time_created}</div>
        </Space>
    );
}

export default ProfileView;
