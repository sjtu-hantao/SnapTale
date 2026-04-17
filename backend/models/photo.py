from pydantic import BaseModel
from typing import Optional, List, BinaryIO
from uuid import UUID, uuid4
from datetime import datetime

class PhotoBase(BaseModel):
    pass
    
class PhotoCreate(PhotoBase):
    device_id: UUID
    location: Optional[str] = None
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    
    class Config:
        arbitrary_types_allowed=True

class PhotoUpdate(PhotoBase):
    photo_id: UUID
    user_id: Optional[UUID] = None
    location: Optional[str] = None
    description: Optional[str] = None
    starred: Optional[bool] = None
    file_name: Optional[str] = None
    
# Update PhotoResponse to fit frontend needs
class PhotoResponse(PhotoBase):
    photo_id: UUID
    user_id: UUID
    device_id: UUID
    time_created: datetime
    time_modified: datetime
    url: Optional[str] = None
    journal_id: Optional[UUID] = None
    description: Optional[str] = None
    file_name: Optional[str] = None
    
    
    class Config:
        from_attributes = True
    