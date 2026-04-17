import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pytest
import json
import requests
import string
import random
from typing import List, Dict, Any
from uuid import UUID
import dashscope
from dotenv import load_dotenv

load_dotenv()

dashscope.api_key = os.environ.get("QWEN_API_KEY")
STATIC_PATH = os.getenv("STATIC_PATH")
STATIC_SERVER = os.getenv("STATIC_SERVER")

SERVER_URL = "http://localhost:8000"


@pytest.fixture
def get_user():
    """
    Returns a user dictionary with a random username and password.
    """
    user_id = '5136d795-1d5f-436c-853b-a8c898ecd426'
    
    response = requests.get(f"{SERVER_URL}/users/{user_id}")
    assert response.status_code == 200
    user = response.json()
    
    assert user["user_id"] == user_id
    assert user['username'] == 'testuser_glduxkebjy'

    return user

def test_get_photos(get_user):
    """
    Test the get_photos endpoint.
    """
    user = get_user
    print(user)
    
    response = requests.get(f"{SERVER_URL}/users/{user['user_id']}/photos")
    
    assert response.status_code == 200
    photos = response.json()
    
    print(photos)
    assert isinstance(photos, list)
    assert len(photos) > 0
    for photo in photos:
        assert photo['user_id'] == user['user_id']
        
# create an empty journal
def test_add_journal(get_user):
    """
    Test the add_journal endpoint.
    """
    user = get_user
    journal = {
        "title": "Test Journal",
        "description": "This is a test journal entry.",
        "tags": ["test", "journal"]
    }
    
    response = requests.post(f"{SERVER_URL}/users/{user['user_id']}/journals", json=journal)
    
    assert response.status_code == 200
    journal_data = response.json()
    
    assert journal_data["title"] == journal["title"]
    assert journal_data["description"] == journal["description"]
    assert journal_data["user_id"] == user["user_id"]
    assert journal_data["journal_id"]
    
    print(journal_data)
    # clean up: delete the journal after the test
    response = requests.delete(f"{SERVER_URL}/users/{user['user_id']}/journals/{journal_data['journal_id']}")
    assert response.status_code == 200
    
    
def test_generate_journal(get_user):
    user = get_user
    
    response = requests.get(f"{SERVER_URL}/users/{user['user_id']}/photos")
    assert response.status_code == 200
    photos = response.json()
     
    sampled_photos = random.sample(photos, 5)
    photo_ids = [photo['photo_id'] for photo in sampled_photos]
    assert type(photo_ids) == list
    
    body = {
        "photo_ids": ["cead0b4d-8e4c-4b36-9b3f-7fa446428b72"]
    }
        
    response = requests.post(f"{SERVER_URL}/users/{user['user_id']}/journals/generate", json=body, headers={"Content-Type": "application/json"})
    assert response.status_code == 200
    journal = response.json()
    print(journal)
    
    assert journal["user_id"] == user["user_id"]
    assert journal["title"]
    assert journal["description"]