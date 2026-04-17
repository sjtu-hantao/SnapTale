import axios from "axios";
import JSZip from "jszip";

interface PhotoResponse {
    photo_id: string;
    time_created: string;
    url?: string | "";
    href?: string | "https://ant.design";
    title?: string | "Undefined";
    tags?: string[] | [];
    description?: string | "";
  }
  
  interface GetUserPhotoOptions {
    starred?: boolean;
    device?: string | null;
    fromDate?: string | null;
    toDate?: string | null;
    contains?: string | null;
  }

  async function getUserPhoto(userId: string, options?: GetUserPhotoOptions, offset?: number, limit?:number): Promise<PhotoResponse[]> {
    try {
      let url = `${window.backend_url}/users/${userId}/photos`;
  
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
      return response.data as PhotoResponse[];
    } catch (error) {
      console.error('Error fetching user journal:', error);
      throw error;
    }
  }


async function deleteUserPhotos(userId: string, photo_ids: string[]): Promise<any> {
    try {
        const baseUrl = `${window.backend_url}/users/${userId}/photos`;
        const deletePromises = photo_ids.map(photoId => axios.delete(`${baseUrl}/${photoId}`));

        const responses = await Promise.all(deletePromises);

        responses.forEach((response, index) => {
            if (response.status !== 200) {
                console.error(`Failed to delete photo ${photo_ids[index]}`);
            }else{
                console.log(`Photo ${photo_ids[index]} deleted`);
            }
        });
    } catch (error) {
        console.error('Error deleting user photos:', error);
        throw error;
    }
}


async function describeUserPhoto(userId: string, photo_id: string): Promise<PhotoResponse> {
    try {
        const baseUrl = `${window.backend_url}/users/${userId}/photos/${photo_id}/analyze`;

        const response = await axios.get(baseUrl);

        if (response.status !== 200) {
            console.error(`Failed to describe photo ${photo_id}`);
        }

        return response.data as PhotoResponse;

    } catch (error) {
        console.error('Error updating user photo:', error);
        throw error;
    }
}

async function downloadSelectedPhotos(userId: string, photoUrls: string[]): Promise<Blob> {
    try {
        const zip = new JSZip();
        const lastModifiedDates: Map<number, string> = new Map(); 

        const downloadPromises = photoUrls.map(async (url, index) => {
            const headers: any = {};
            const lastModifiedDate = lastModifiedDates.get(index);
            // Add the If-Modified-Since header if we have a last modified date
            if (lastModifiedDate) {
                headers['If-Modified-Since'] = lastModifiedDate;
            }

            try {
                const response = await axios.get(`http://${url}`, {
                    responseType: 'blob',
                    headers,
                });

                if (response.status === 200) { // OK

                    const newLastModifiedDate = response.headers['last-modified'];
                    if (newLastModifiedDate) {
                        lastModifiedDates.set(index, newLastModifiedDate);
                    }

                    zip.file(`photo_${index}.png`, response.data);
                } else if (response.status === 304) { // Not Modified
                    console.log(`Photo ${index} not modified, skipping.`);
                    // Optionally handle the unmodified case here
                } else {
                    throw new Error(`Unexpected response status: ${response.status}`);
                }
            } catch (error) {
                console.error(`Error downloading photo ${index}:`, error);
                // Handle individual photo download errors if needed
            }
        });

        await Promise.all(downloadPromises);

        // Generate the ZIP file
        const zipBlob = await zip.generateAsync({ type: 'blob' });

        return zipBlob;

    } catch (error) {
        console.error('Error creating zip file:', error);
        throw error;
    }
}


async function generateJournalFromPhotos(userId: string, photoIds: string[]): Promise<any> {
    try {
        // Prepare the request body
        const body = {
            photo_ids: photoIds,
        };

        // Make a POST request to generate the journal
        const response = await axios.post(
            `${window.backend_url}/users/${userId}/journals/generate`,
            body,
            {
                headers: {
                    'Content-Type': 'application/json',
                },
            }
        );

        if (response.status !== 200) {
            console.error('Failed to generate journal');
        } 

        return response.data;

    } catch (error) {
        console.error('Error generating journal from photos:', error);
        throw error;
    }
}

export default getUserPhoto;
export { deleteUserPhotos, describeUserPhoto, downloadSelectedPhotos, generateJournalFromPhotos };
export type { PhotoResponse };