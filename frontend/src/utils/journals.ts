import axios from 'axios';

interface JournalResponse {
  id: string;
  datetime: string;
  content?: string | "";
  title?: string | "Undefined";
  tags?: string[] | [];
  description?: string | "";
  journal_id: string;
  starred: boolean | false;
  time_created: string;
  time_modified: string;
  cover?: string | null;
}

interface GetUserJournalOptions {
  starred?: boolean;
  device?: string | null;
  fromDate?: string | null;
  toDate?: string | null;
  contains?: string | null;
}

async function getUserJournal(userId: string, options?: GetUserJournalOptions, offset?: number, limit?:number): Promise<JournalResponse[]> {
  try {
    let url = `${window.backend_url}/users/${userId}/journals`;

    // 构建查询参数
    if (options) {
      const params = new URLSearchParams();
      if (options.starred) {
        params.append('starred', 'true');
      }
      if (options.device) {
        params.append('device', options.device);
      }
      if (options.fromDate) {
        params.append('fromDate', options.fromDate);
      }
      if (options.toDate) {
        params.append('toDate', options.toDate);
      }
      if (options.contains) {
        params.append('contains', options.contains);
      }
      if (offset) {
        params.append('offset', offset.toString());
      }
      if (limit) {
        params.append('limit', limit.toString());
      }
      url += `?${params.toString()}`;
      console.log('url:', url);
    }

    const response = await axios.get(url);
    return response.data as JournalResponse[];
  } catch (error) {
    console.error('Error fetching user journal:', error);
    throw error;
  }
}

async function toggleUserJournalStar(userId: string, entryId: string, is_starred: boolean): Promise<void> {
    try {
        const url = `${window.backend_url}/users/${userId}/journals/${entryId}`;
        const data = { starred: !is_starred };
        console.log('data:', data);
        const response = await axios.put(url, data, { headers: { 'Content-Type': 'application/json' } });
        console.log('User journal starred:', response.data);
    } catch (error) {
        console.error('Error starring user journal:', error);
        throw error;
    }
}


async function updateUserJournal(userId: string, entry: JournalResponse): Promise<void> {
    try {
        const url = `${window.backend_url}/users/${userId}/${entry.id}`;
        const response = await axios.put(url, entry);
        console.log('User journal updated:', response.data);
    } catch (error) {
        console.error('Error updating user journal:', error);
        throw error;
    }
}


async function deleteUserJournal(userId: string, entryId: number): Promise<JournalResponse> {
    try {
        const url = `${window.backend_url}/users/${userId}/journals/${entryId}`;
        const response = await axios.delete(url);
        console.log('User journal deleted:', response.data);
        return response.data as JournalResponse;
    } catch (error) {
        console.error('Error deleting user journal:', error);
        throw error;
    }
}


async function addUserJournal(userId: string): Promise<JournalResponse> {
    try {
        const url = `${window.backend_url}/users/${userId}/journals/`;
        const entry = {
            title: 'New Journal',
            description: '# New Journal',
        };
        const response = await axios.post(url, entry);
        console.log('User journal added:', response.data);
        return response.data as JournalResponse;
    } catch (error) {
        console.error('Error adding user journal:', error);
        throw error;
    }
}

export default getUserJournal;
export { updateUserJournal, deleteUserJournal, addUserJournal, toggleUserJournalStar };
export type { JournalResponse, GetUserJournalOptions };