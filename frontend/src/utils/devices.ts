import axios from "axios";


interface DeviceResponse {
    device_id: string;
    user_id: string;
    api_key: string;
    time_created: Date;
    time_modified: Date;
    device_name: string;
    is_active: boolean;
}


async function getUserDevices(userId: string): Promise<DeviceResponse[]> {
    try {
        const url = `/api/devices/${userId}`;
        const response = await axios.get(url);
        console.log('User devices:', response.data);
        return response.data as DeviceResponse[]; // 明确返回类型
    } catch (error) {
        console.error('Error fetching user devices:', error);
        throw error;
    }
}


export default getUserDevices;
export type { DeviceResponse };