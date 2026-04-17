import sys, os
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
        "password": f"password123"}
    
    response = requests.post(f"{SERVER_URL}/users", json=test_user, headers={"Content-Type": "application/json"})
    user_data = response.json()
    yield user_data
    
    requests.delete(f"{SERVER_URL}/users/{user_data['user_id']}")

def test_get_user(create_test_user):
    """
    Test case for getting a user via GET request.
    """
    user = create_test_user
    response = requests.get(f"{SERVER_URL}/users/{user['user_id']}", headers={"Content-Type": "application/json"})
    
    assert response.status_code == 200
    user_data = response.json()
    assert user_data["user_id"] == user["user_id"]
    assert user_data["username"] == user["username"]
    
def test_update_user(create_test_user):
    """
    Test case for updating a user via PUT request
    """
    user = create_test_user
    new_data = {
        "bio": "Hi!"
    }
    
    response = requests.put(f"{SERVER_URL}/users/{user['user_id']}", json=new_data, headers={"Content-Type": "application/json"})
    
    assert response.status_code == 200
    user_data = response.json()
    assert user_data["user_id"] == user["user_id"]
    assert user_data["username"] == user["username"]
    assert user_data["bio"] == new_data["bio"]
    
    
def test_delete_user(create_test_user):
    """
    Test case for deleting a user via DELETE request
    """
    user = create_test_user
    response = requests.delete(f"{SERVER_URL}/users/{user['user_id']}", headers={"Content-Type": "application/json"})
    
    assert response.status_code == 200
    assert response.json() == {"message": "User deleted successfully"}
    
    response = requests.get(f"{SERVER_URL}/users/{user['user_id']}", headers={"Content-Type": "application/json"})
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}