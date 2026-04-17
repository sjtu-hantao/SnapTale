import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pytest
import json
import requests
import string
import random

SERVER_URL = "http://localhost:8000"

def random_string(length=10):
    """Generate a random string of fixed length"""
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

@pytest.fixture(scope="function")
def create_test_user():
    """
    Create a test user
    """
    test_user = {
        "username": f"testuser_{random_string()}",
        "email": f"{random_string()}@test.com",
        "password": "password123"
    }
    
    response = requests.post(f"{SERVER_URL}/users", json=test_user, headers={"Content-Type": "application/json"})
    user_data = response.json()
    yield user_data
    
    # Clean up: Delete the user after the test
    response = requests.delete(f"{SERVER_URL}/users/{user_data['user_id']}")
    assert response.status_code == 200
    
    
def test_create_device(create_test_user):
    
    user = create_test_user
    device = {
        "device_name": "testdevice",
        "device_type": "Arduino",
        "app_version": "1.0",
        "api_key": f"testapikey{random_string()}",
        }
    user_id = user["user_id"]
    response = requests.post(f"{SERVER_URL}/users/{user_id}/devices", json=device, headers={"Content-Type": "application/json"})
    
    assert response.status_code == 200
    device_data = response.json()
    assert device_data["device_name"] == device["device_name"]
    assert device_data["device_id"]
    assert device_data["user_id"] == user["user_id"]
    assert device_data["api_key"] == device["api_key"]
    
    # clean up: delete the device after the test
    response = requests.delete(f"{SERVER_URL}/users/{device_data['user_id']}/devices/{device_data['device_id']}")
    print(response.json())
    assert response.status_code == 200
    
