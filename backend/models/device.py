from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID, uuid4
from datetime import datetime

class DeviceBase(BaseModel):
    pass

class DeviceCreate(DeviceBase):
    device_name: str
    device_type: Optional[str] = None
    api_key: str
    os_type: Optional[str] = None
    os_version: Optional[str] = None
    app_version: Optional[str] = None
    
    
class DeviceUpdate(DeviceBase):    
    is_active: Optional[bool] = None
    api_key: Optional[str] = None
    device_name: Optional[str] = None
    device_type: Optional[str] = None
    os_type: Optional[str] = None
    os_version: Optional[str] = None
    app_version: Optional[str] = None
    
    
class DeviceResponse(DeviceBase):
    device_id: UUID
    user_id: UUID
    api_key: str
    time_created: datetime
    time_modified: datetime
    device_name: str
    is_active: bool
    
    class Config:
        from_attributes = True