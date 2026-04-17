from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID, uuid4
from datetime import datetime

class EntryBase(BaseModel):
    pass

class EntryCreate(EntryBase):
    content: str
    
class EntryUpdate(EntryBase):
    user_id: Optional[UUID] = None
    journal_id: Optional[UUID] = None
    entry_id: UUID
    content: Optional[str] = None
    
    
class EntryResponse(EntryBase):
    entry_id: UUID
    user_id: UUID
    journal_id: UUID
    time_created: datetime
    time_modified: datetime
    content: str
    
    class Config:
        from_attributes = True