from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from models import User, Device, Journal, Photo, Entry, get_db
from .schemas import (UserCreate, UserUpdate, UserResponse, 
                     DeviceCreate, DeviceUpdate, DeviceResponse,
                     JournalCreate, JournalUpdate, JournalResponse,
                     PhotoCreate, PhotoUpdate, PhotoResponse,
                     EntryCreate, EntryUpdate, EntryResponse)

from .functions import hash_pwd, describe_image

router = APIRouter()

# User endpoints
@router.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # create new user
    password_hash = hash_pwd(user.password)
    del user.password
    db_user = User(**user.dict(), password_hash=password_hash)
    
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error creating user")
    
    return db_user

@router.get("/users/", response_model=List[UserResponse])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.get("/users/{user_id}", response_model=UserResponse)
def read_user(user_id: UUID, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.user_id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: UUID, user: UserUpdate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.user_id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    for key, value in user.dict(exclude_unset=True).items():
        setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.delete("/users/{user_id}", response_model=UserResponse)
def delete_user(user_id: UUID, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.user_id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    return db_user

# Device endpoints
@router.post("/devices/", response_model=DeviceResponse)
def create_device(device: DeviceCreate, db: Session = Depends(get_db)):
    db_device = Device(**device.dict())
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device

@router.get("/devices/", response_model=List[DeviceResponse])
def read_devices(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    devices = db.query(Device).offset(skip).limit(limit).all()
    return devices

@router.get("/devices/{device_id}", response_model=DeviceResponse)
def read_device(device_id: UUID, db: Session = Depends(get_db)):
    db_device = db.query(Device).filter(Device.device_id == device_id).first()
    if db_device is None:
        raise HTTPException(status_code=404, detail="Device not found")
    return db_device

@router.put("/devices/{device_id}", response_model=DeviceResponse)
def update_device(device_id: UUID, device: DeviceUpdate, db: Session = Depends(get_db)):
    db_device = db.query(Device).filter(Device.device_id == device_id).first()
    if db_device is None:
        raise HTTPException(status_code=404, detail="Device not found")
    for key, value in device.dict(exclude_unset=True).items():
        setattr(db_device, key, value)
    db.commit()
    db.refresh(db_device)
    return db_device

@router.delete("/devices/{device_id}", response_model=DeviceResponse)
def delete_device(device_id: UUID, db: Session = Depends(get_db)):
    db_device = db.query(Device).filter(Device.device_id == device_id).first()
    if db_device is None:
        raise HTTPException(status_code=404, detail="Device not found")
    db.delete(db_device)
    db.commit()
    return db_device

# Journal endpoints
@router.post("/users/{userId}/journals", response_model=JournalResponse)
def create_journal(journal: JournalCreate, userId: UUID, db: Session = Depends(get_db)):
    db_journal = Journal(**journal.dict(), user_id=userId.bytes)
    db.add(db_journal)
    db.commit()
    db.refresh(db_journal)
    return db_journal

@router.get("/users/{userId}/journals")
def read_journals(userId: UUID, db: Session = Depends(get_db)):
    # Check if user exists
    if db.query(User).filter(User.user_id == userId.bytes).first() is None:
        raise HTTPException(status_code=404, detail=f"User {userId} not found")
    
    # Query journals with pagination
    journals = db.query(Journal).filter(Journal.user_id == userId.bytes).all()
    return journals

# @router.get("/journals/", response_model=List[JournalResponse])
# def read_journals(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     journals = db.query(Journal).offset(skip).limit(limit).all()
#     return journals

@router.get("/journals/{journal_id}", response_model=JournalResponse)
def read_journal(journal_id: UUID, db: Session = Depends(get_db)):
    db_journal = db.query(Journal).filter(Journal.journal_id == journal_id).first()
    if db_journal is None:
        raise HTTPException(status_code=404, detail="Journal not found")
    return db_journal

@router.put("/journals/{journal_id}", response_model=JournalResponse)
def update_journal(journal_id: UUID, journal: JournalUpdate, db: Session = Depends(get_db)):
    db_journal = db.query(Journal).filter(Journal.journal_id == journal_id).first()
    if db_journal is None:
        raise HTTPException(status_code=404, detail="Journal not found")
    for key, value in journal.dict(exclude_unset=True).items():
        setattr(db_journal, key, value)
    db.commit()
    db.refresh(db_journal)
    return db_journal

@router.delete("/journals/{journal_id}", response_model=JournalResponse)
def delete_journal(journal_id: UUID, db: Session = Depends(get_db)):
    db_journal = db.query(Journal).filter(Journal.journal_id == journal_id).first()
    if db_journal is None:
        raise HTTPException(status_code=404, detail="Journal not found")
    db.delete(db_journal)
    db.commit()
    return db_journal

# Photo endpoints

# post a new photo for a user
@router.post("/user/{userId}/photos", response_model=PhotoResponse)
def create_photo(photo: PhotoCreate, userId: UUID, db: Session = Depends(get_db)):
    # store photo locally 
    base64_string = photo.base64
    url = string2url(base64_string, photo.photo_id)
        
    if url is None:
        raise HTTPException(status_code=400, detail="Invalid image format, failed to store image locally")
        
    del photo.base64
    
    db_photo = Photo(**photo.dict(), url=url)
    db.add(db_photo)
    db.commit()
    db.refresh(db_photo)
    return db_photo

@router.get("/photos/", response_model=List[PhotoResponse])
def read_photos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    photos = db.query(Photo).offset(skip).limit(limit).all()
    return photos

@router.get("/photos/{photo_id}", response_model=PhotoResponse)
def read_photo(photo_id: UUID, db: Session = Depends(get_db)):
    db_photo = db.query(Photo).filter(Photo.photo_id == photo_id).first()
    if db_photo is None:
        raise HTTPException(status_code=404, detail="Photo not found")
    return db_photo

@router.put("/photos/{photo_id}", response_model=PhotoResponse)
def update_photo(photo_id: UUID, photo: PhotoUpdate, db: Session = Depends(get_db)):
    db_photo = db.query(Photo).filter(Photo.photo_id == photo_id).first()
    if db_photo is None:
        raise HTTPException(status_code=404, detail="Photo not found")
    for key, value in photo.dict(exclude_unset=True).items():
        setattr(db_photo, key, value)
    db.commit()
    db.refresh(db_photo)
    return db_photo

@router.delete("/photos/{photo_id}", response_model=PhotoResponse)
def delete_photo(photo_id: UUID, db: Session = Depends(get_db)):
    db_photo = db.query(Photo).filter(Photo.photo_id == photo_id).first()
    if db_photo is None:
        raise HTTPException(status_code=404, detail="Photo not found")
    db.delete(db_photo)
    db.commit()
    return db_photo

@router.get("/photos/{photo_id}/analyze", response_model=PhotoResponse)
def analyze_photo(photo_id: UUID, db: Session = Depends(get_db)):
    db_photo = db.query(Photo).filter(Photo.photo_id == photo_id).first()
    if db_photo is None:
        raise HTTPException(status_code=404, detail="Photo not found")
    # Call image analysis function
    db_photo.description = describe_image(db_photo.url)
    
    # Update db_photo with analysis results
    db.commit()
    db.refresh(db_photo)
    return db_photo


# Entry endpoints
@router.post("/entries/", response_model=EntryResponse)
def create_entry(entry: EntryCreate, db: Session = Depends(get_db)):
    db_entry = Entry(**entry.dict())
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry

@router.get("/entries/", response_model=List[EntryResponse])
def read_entries(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    entries = db.query(Entry).offset(skip).limit(limit).all()
    return entries

@router.get("/entries/{entry_id}", response_model=EntryResponse)
def read_entry(entry_id: UUID, db: Session = Depends(get_db)):
    db_entry = db.query(Entry).filter(Entry.entry_id == entry_id).first()
    if db_entry is None:
        raise HTTPException(status_code=404, detail="Entry not found")
    return db_entry

@router.put("/entries/{entry_id}", response_model=EntryResponse)
def update_entry(entry_id: UUID, entry: EntryUpdate, db: Session = Depends(get_db)):
    db_entry = db.query(Entry).filter(Entry.entry_id == entry_id).first()
    if db_entry is None:
        raise HTTPException(status_code=404, detail="Entry not found")
    for key, value in entry.dict(exclude_unset=True).items():
        setattr(db_entry, key, value)
    db.commit()
    db.refresh(db_entry)
    return db_entry

@router.delete("/entries/{entry_id}", response_model=EntryResponse)
def delete_entry(entry_id: UUID, db: Session = Depends(get_db)):
    db_entry = db.query(Entry).filter(Entry.entry_id == entry_id).first()
    if db_entry is None:
        raise HTTPException(status_code=404, detail="Entry not found")
    db.delete(db_entry)
    db.commit()
    return db_entry