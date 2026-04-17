import { useState, useEffect } from 'react';
import apiClient from './axiosInstance';
import { message } from 'antd';

interface PhotoType {
    photo_id: string;
    user_id?: string;
    device_id?: string;
    time_created: string;
    time_modified?: string;
    url: string;
    journal_id?: string;
    description?: string;
    file_name?: string;
  }

  interface Data {
    userId: string;
  }

const handleAllPhotos = async ({ data }: { data: Data }): Promise<PhotoType[] | undefined> => {
    let url =  `/users/${data.userId}/photos`;
    
    try {
        const response = await apiClient.get<PhotoType[]>(url);
        return response.data;
        
      } catch (error) {
        console.error('Error fetching photos:', error);
      }
};

export default handleAllPhotos;