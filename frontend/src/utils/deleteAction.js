import apiClient from '../../../utils/axiosInstance';
import { message } from 'antd';

const handleDelete = ({ data }) => {
    let url = '';
    if (data.type === 'photo') {
        url = `/user/${data.userId}/photos/${data.id}`;
    } else if (data.type === 'journal') {
        url = `/user/${data.userId}/journals/${data.id}`;
    }
    else {
        console.error('Error: Invalid data type!');
    }
    apiClient.delete(url)
        .then(() => {
            window.location.reload(); // 刷新页面
            message.success(`Deleted!`);
        })
        .catch(error => {
            console.error('Error deleting data:', error);
        });
};

export default handleDelete;