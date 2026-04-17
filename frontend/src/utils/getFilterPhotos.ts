import apiClient from './axiosInstance';
import { SearchFilters } from '../components/SearchBar/SearchBar';

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

interface QueryType { 
    user_id?: string| null;
    limit?: number| null;
    offset?: number| null;
    filters?: SearchFilters;
}

interface formalQueryType {
    user_id?: string| null;
    limit?: number| null;
    offset?: number| null;
    starred?: boolean;
    device?: string | null;
    fromDate?: string | null;
    toDate?: string | null ;
    contains?: string | null;
}

const handleFilterPhotos = async ({ query }: {  query: any }): Promise<PhotoType[] | undefined> => {
  console.log("before query", query);
  let url =  `/users/${query.user_id}/photos`;

  let formalQuery: formalQueryType = {
    user_id: query.user_id,
    limit: query.limit, // Can be obtained by the length of data
    offset: query.offset,
    starred: query.filters.starred,
    device: window.device_id,
    fromDate: query.filters.fromDate,
    toDate: query.filters.toDate,
    contains: query.filters.contains,
  }


  try {
    console.log("formalQuery", formalQuery);
    const response = await apiClient.get<PhotoType[]>(url, { params: formalQuery });
    return response.data;
  } catch (error) {
    console.error('Error fetching photos:', error);
  }
};

export default handleFilterPhotos;
export type { QueryType , SearchFilters, PhotoType };