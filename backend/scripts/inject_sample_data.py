import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


import json
import requests
import string
import random
import time

SERVER_URL = "http://localhost:8000"

def random_string(length=10):
    """Generate a random string of fixed length"""
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

# create sample user

test_user = {
        "username": f"testuser_{random_string()}",
        "email": f"{random_string()}@test.com",
        "password": "password123"
    }

response = requests.post(f"{SERVER_URL}/users", json=test_user, headers={"Content-Type": "application/json"})
test_user = response.json()



# create sample device

test_device = {
        "device_name": f"testdevice_{random_string()}",
        "device_type": "Arduino",
        "os_version": "14.0",
        "app_version": "1.0",
        "api_key": f"{random_string()}"
    }


response = requests.post(f"{SERVER_URL}/users/{test_user['user_id']}/devices", json=test_device, headers={"Content-Type": "application/json"})
test_device = response.json()

# upload 40 sample photos

filepath = os.path.join(os.path.dirname(__file__), "../tests/testimage.jpg")

for i in range(3):
    with open(filepath, "rb") as image_file:
        files = {"image": ("testimage.jpg", open(filepath, "rb"), "image/jpeg")}
        photo_create = {
            "device_id": test_device["device_id"],
            "location": "Test Location",
            "file_name": "testimage.jpg",
            "file_size": 1024,
            "file_type": "jpg"
        }
        
        data = {
                "photo_create": json.dumps(photo_create)
            }
        
        response = requests.post(f"{SERVER_URL}/users/{test_device['user_id']}/photos", files=files, data=data)
        print(f"{(i)} Response:", response.text)
        
        # analyze photo
        if response.status_code == 200:
            photo = response.json()
            response = requests.get(f"{SERVER_URL}/users/{test_user['user_id']}/photos/{photo['photo_id']}/analyze")
            print(f"{(i)} Analysis Response:", response.text)
            time.sleep(1)

# create sample journal

for i in range(5):
    test_journal = {
        "title": f"Test Journal {i}",
        "content": f"This is a test journal {i}",
        "is_public": True
    }

    response = requests.post(f"{SERVER_URL}/users/{test_user['user_id']}/journals", json=test_journal, headers={"Content-Type": "application/json"})
    test_journal = response.json()
    print(f"Journal {i}:", test_journal)