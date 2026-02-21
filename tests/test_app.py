from copy import deepcopy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

@pytest.fixture(autouse=True)
def reset_activities():
    # Arrange: preserve original activities, then restore after test
    original = deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)

@pytest.fixture
def client():
    return TestClient(app)

def test_get_activities(client):
    # Arrange: (fixture provides initial state)
    # Act
    resp = client.get("/activities")
    # Assert
    assert resp.status_code == 200
    data = resp.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)

def test_signup_success(client):
    # Arrange
    activity = "Chess Club"
    email = "newstudent@mergington.edu"
    assert email not in activities[activity]["participants"]
    # Act
    url = f"/activities/{quote(activity, safe='')}/signup"
    resp = client.post(url, params={"email": email})
    # Assert
    assert resp.status_code == 200
    assert email in activities[activity]["participants"]
    assert resp.json()["message"] == f"Signed up {email} for {activity}"

def test_signup_duplicate(client):
    # Arrange
    activity = "Chess Club"
    email = "michael@mergington.edu"  # already signed up in initial data
    assert email in activities[activity]["participants"]
    # Act
    url = f"/activities/{quote(activity, safe='')}/signup"
    resp = client.post(url, params={"email": email})
    # Assert
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Studentalready signed up for this activity"

def test_unregister_success(client):
    # Arrange
    activity = "Chess Club"
    email = "michael@mergington.edu"
    assert email in activities[activity]["participants"]
    # Act
    url = f"/activities/{quote(activity, safe='')}/signup"
    resp = client.delete(url, params={"email": email})
    # Assert
    assert resp.status_code == 200
    assert email not in activities[activity]["participants"]
    assert resp.json()["message"] == f"Unregistered {email} from {activity}"

def test_unregister_not_found(client):
    # Arrange
    activity = "Chess Club"
    email = "notfound@mergington.edu"
    assert email not in activities[activity]["participants"]
    # Act
    url = f"/activities/{quote(activity, safe='')}/signup"
    resp = client.delete(url, params={"email": email})
    # Assert
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Student not found in activity"
