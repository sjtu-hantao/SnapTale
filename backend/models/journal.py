from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID, uuid4
from datetime import datetime


class JournalBase(BaseModel):
    title: str

class JournalCreate(JournalBase):
    description: Optional[str] = None
    
    
class JournalUpdate(JournalBase):
    title: Optional[str] = None
    starred: Optional[bool] = None
    tags : Optional[List[str]] = None
    is_public: Optional[bool] = None
    description: Optional[str] = None

class JournalResponse(JournalBase):
    journal_id: UUID
    user_id: UUID
    time_created: datetime
    time_modified: datetime
    description: Optional[str] = None
    starred: Optional[bool] = None
    tags : Optional[List[str]] = None
    is_public: Optional[bool] = None
    
    class Config:
        from_attributes = True

