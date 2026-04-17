from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID, uuid4
from datetime import datetime

class UserBase(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    
    
class UserCreate(UserBase):
    password: str
    
class UserUpdate(UserBase):
    password: Optional[str] = None
    is_active: Optional[bool] = None
    profile_picture_url: Optional[str] = None
    bio: Optional[str] = None
    
    
class UserLogin(UserBase):
    email: str
    password: str
    
class UserResponse(UserBase):
    user_id: UUID
    username: str
    email: str
    is_active: bool
    time_created: datetime
    last_login: Optional[datetime]
    profile_picture_url: Optional[str]
    bio: Optional[str]
    
    class Config:
        from_attributes = True
        
        
class ActivityResponse(BaseModel):
    date: str
    count: int
