import copy
import pytest
from fastapi.testclient import TestClient

import src.app as app_module
from src.app import app

client = TestClient(app, follow_redirects=False)


@pytest.fixture(autouse=True)
def reset_activities():
    """Restore in-memory activities state between every test."""
    original = copy.deepcopy(app_module.activities)
    yield
    app_module.activities.clear()
    app_module.activities.update(original)


# ---------------------------------------------------------------------------
# GET /
# ---------------------------------------------------------------------------

def test_root_redirect():
    # Arrange
    # No preconditions needed

    # Act
    response = client.get("/")

    # Assert
    assert response.status_code in (301, 302, 307, 308)
    assert "/static/index.html" in response.headers["location"]


# ---------------------------------------------------------------------------
# GET /activities
# ---------------------------------------------------------------------------

def test_get_activities_returns_200():
    # Arrange
    # No preconditions needed

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200


def test_get_activities_has_all_nine_activities():
    # Arrange
    # No preconditions needed

    # Act
    response = client.get("/activities")

    # Assert
    data = response.json()
    assert len(data) == 9


def test_get_activities_structure():
    # Arrange
    required_keys = {"description", "schedule", "max_participants", "participants"}

    # Act
    response = client.get("/activities")

    # Assert
    data = response.json()
    for activity in data.values():
        assert required_keys.issubset(activity.keys())


# ---------------------------------------------------------------------------
# POST /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

def test_signup_success():
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert email in data["message"]
    assert activity_name in data["message"]


def test_signup_activity_not_found():
    # Arrange
    activity_name = "Nonexistent Activity"
    email = "student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# DELETE /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

def test_unregister_success():
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert email in data["message"]
    assert activity_name in data["message"]


def test_unregister_activity_not_found():
    # Arrange
    activity_name = "Nonexistent Activity"
    email = "student@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404


def test_unregister_participant_not_found():
    # Arrange
    activity_name = "Chess Club"
    email = "notregistered@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
