# database.py
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv
from sqlalchemy import Column, Text
from sqlmodel import Field, Relationship, SQLModel, Session, create_engine

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[1]
STORAGE_DIR = BASE_DIR / "storage"
STORAGE_DIR.mkdir(parents=True, exist_ok=True)

default_db_path = STORAGE_DIR / "snaptale_mvp.db"
DB_URL = os.getenv("DB_URL") or f"sqlite:///{default_db_path.as_posix()}"

engine_kwargs = {}
if DB_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(DB_URL, **engine_kwargs)

# Function to get a database session
def get_db() -> Session:
    with Session(engine) as session:
        yield session

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    print("Tables ensured")


def reset_db_and_tables():
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    print("Tables reset")

class User(SQLModel, table=True):
    __tablename__ = 'users'
    
    user_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    username: str = Field(max_length=255, unique=False, nullable=False)
    email: str = Field(max_length=255, unique=True, nullable=False)
    password_hash: str = Field(max_length=255, nullable=False)
    time_created: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = Field(default=None)
    is_active: bool = Field(default=True)
    profile_picture_url: Optional[str] = Field(max_length=255, default=None)
    bio: Optional[str] = Field(default=None)

    devices: List["Device"] = Relationship(back_populates="user")
    journals: List["Journal"] = Relationship(back_populates="user")
    photos: List["Photo"] = Relationship(back_populates="user")
    entries: List["Entry"] = Relationship(back_populates="user")

class Device(SQLModel, table=True):
    __tablename__ = 'devices'
    
    
    device_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.user_id")
    
    device_name: str = Field(max_length=255, default=None)
    device_type: Optional[str] = Field(max_length=255, default=None)
    os_type: Optional[str] = Field(max_length=255, default=None)
    os_version: Optional[str] = Field(max_length=255, default=None)
    app_version: Optional[str] = Field(max_length=255, default=None)
    
    last_sync: Optional[datetime] = Field(default=None)
    is_active: bool = Field(default=True)
    
    api_key: str = Field(max_length=255, unique=True)
    time_created: datetime = Field(default_factory=datetime.utcnow)
    time_modified: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})

    user: "User" = Relationship(back_populates="devices")
    photos: List["Photo"] = Relationship(back_populates="device")
    entries: List["Entry"] = Relationship(back_populates="device")

class Journal(SQLModel, table=True):
    __tablename__ = 'journals'
    

    journal_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.user_id")
    title: str = Field(max_length=255, nullable=False)
    description: Optional[str] = Field(default=None, sa_column=Column(Text))
    time_created: datetime = Field(default_factory=datetime.utcnow)
    time_modified: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})
    starred: bool = Field(default=False)

    user: "User" = Relationship(back_populates="journals")
    entries: List["Entry"] = Relationship(back_populates="journal")
    photos: List["Photo"] = Relationship(back_populates="journal")

class Photo(SQLModel, table=True):
    __tablename__ = 'photos'
    

    photo_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.user_id")
    journal_id: Optional[uuid.UUID] = Field(foreign_key="journals.journal_id")
    device_id: uuid.UUID = Field(foreign_key="devices.device_id")
    time_created: datetime = Field(default_factory=datetime.utcnow)
    time_modified: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})
    location: Optional[str] = Field(max_length=255, default=None)
    description: Optional[str] = Field(default=None, sa_column=Column(Text))
    url: str = Field(max_length=255)
    starred: bool = Field(default=False)
    file_name: Optional[str] = Field(max_length=255, default=None)
    file_size: Optional[int] = Field(default=None)
    file_type: Optional[str] = Field(max_length=255, default=None)

    user: "User" = Relationship(back_populates="photos")
    journal: "Journal" = Relationship(back_populates="photos")
    device: "Device" = Relationship(back_populates="photos")

class Entry(SQLModel, table=True):
    __tablename__ = 'entries'
    

    entry_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.user_id")
    journal_id: uuid.UUID = Field(foreign_key="journals.journal_id")
    device_id: uuid.UUID = Field(foreign_key="devices.device_id")
    time_created: datetime = Field(default_factory=datetime.utcnow)
    time_modified: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})
    position: Optional[str] = Field(max_length=255, default=None)
    content: Optional[str] = Field(default=None, sa_column=Column(Text))

    user: "User" = Relationship(back_populates="entries")
    journal: "Journal" = Relationship(back_populates="entries")
    device: "Device" = Relationship(back_populates="entries")


class UserPreference(SQLModel, table=True):
    __tablename__ = "user_preferences"

    preference_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.user_id", unique=True, index=True)
    style_weights_json: str = Field(default="{}", sa_column=Column(Text))
    top_tags_json: str = Field(default="[]", sa_column=Column(Text))
    voice_notes_json: str = Field(default="[]", sa_column=Column(Text))
    exemplar_quotes_json: str = Field(default="[]", sa_column=Column(Text))
    summary: str = Field(default="", sa_column=Column(Text))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow},
    )


class PhotoCollection(SQLModel, table=True):
    __tablename__ = "photo_collections"

    collection_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.user_id", index=True)
    title: str = Field(default="Untitled Moment", max_length=255)
    context: str = Field(default="", sa_column=Column(Text))
    story_summary: str = Field(default="", sa_column=Column(Text))
    narrative_arc: str = Field(default="", sa_column=Column(Text))
    emotional_tone: str = Field(default="steady", max_length=64)
    retrieved_memory_ids_json: str = Field(default="[]", sa_column=Column(Text))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow},
    )


class CollectionAsset(SQLModel, table=True):
    __tablename__ = "collection_assets"

    asset_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    collection_id: uuid.UUID = Field(foreign_key="photo_collections.collection_id", index=True)
    user_id: uuid.UUID = Field(foreign_key="users.user_id", index=True)
    file_name: str = Field(max_length=255)
    file_path: str = Field(max_length=1024)
    public_url: str = Field(max_length=1024)
    analysis_text: str = Field(default="", sa_column=Column(Text))
    mood_tag: str = Field(default="neutral", max_length=64)
    metadata_json: str = Field(default="{}", sa_column=Column(Text))
    created_at: datetime = Field(default_factory=datetime.utcnow)


class GeneratedPost(SQLModel, table=True):
    __tablename__ = "generated_posts"

    post_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    collection_id: uuid.UUID = Field(foreign_key="photo_collections.collection_id", index=True)
    user_id: uuid.UUID = Field(foreign_key="users.user_id", index=True)
    style_name: str = Field(max_length=128, index=True)
    hook: str = Field(default="", sa_column=Column(Text))
    content: str = Field(default="", sa_column=Column(Text))
    prompt_snapshot: str = Field(default="", sa_column=Column(Text))
    is_selected: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class FeedbackEvent(SQLModel, table=True):
    __tablename__ = "feedback_events"

    feedback_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.user_id", index=True)
    collection_id: uuid.UUID = Field(foreign_key="photo_collections.collection_id", index=True)
    post_id: uuid.UUID = Field(foreign_key="generated_posts.post_id", index=True)
    signal_type: str = Field(max_length=64)
    rating: Optional[int] = Field(default=None)
    tags_json: str = Field(default="[]", sa_column=Column(Text))
    rewrite_text: str = Field(default="", sa_column=Column(Text))
    created_at: datetime = Field(default_factory=datetime.utcnow)


class MemoryItem(SQLModel, table=True):
    __tablename__ = "memory_items"

    memory_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.user_id", index=True)
    collection_id: Optional[uuid.UUID] = Field(
        default=None,
        foreign_key="photo_collections.collection_id",
        index=True,
    )
    source_type: str = Field(default="collection_story", max_length=64)
    title: str = Field(default="", max_length=255)
    summary: str = Field(default="", sa_column=Column(Text))
    emotion: str = Field(default="steady", max_length=64)
    growth_signal: str = Field(default="consistency", max_length=128)
    content: str = Field(default="", sa_column=Column(Text))
    keywords_json: str = Field(default="[]", sa_column=Column(Text))
    strength: float = Field(default=1.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
