import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(
        app_module,
        "activities",
        {
            "Test Activity": {
                "description": "A test activity",
                "schedule": "Mondays, 3:00 PM",
                "max_participants": 3,
                "participants": ["existing@example.edu"],
            }
        },
    )
    return TestClient(app_module.app)


def test_get_activities_returns_activity_data(client):
    # Arrange

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "Test Activity": {
            "description": "A test activity",
            "schedule": "Mondays, 3:00 PM",
            "max_participants": 3,
            "participants": ["existing@example.edu"],
        }
    }


def test_signup_adds_participant(client):
    # Arrange
    email = "new@example.edu"

    # Act
    response = client.post(
        "/activities/Test Activity/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {email} for Test Activity"
    }
    assert email in client.get("/activities").json()["Test Activity"]["participants"]


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    email = "existing@example.edu"

    # Act
    response = client.post(
        "/activities/Test Activity/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student already signed up for this activity"
    }


def test_signup_rejects_unknown_activity(client):
    # Arrange
    activity = "Unknown"
    email = "student@example.edu"

    # Act
    response = client.post(
        f"/activities/{activity}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_removes_participant(client):
    # Arrange
    email = "existing@example.edu"

    # Act
    response = client.delete(
        "/activities/Test Activity/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Unregistered {email} from Test Activity"
    }
    assert email not in client.get("/activities").json()["Test Activity"]["participants"]


def test_unregister_rejects_unknown_participant(client):
    # Arrange
    email = "unknown@example.edu"

    # Act
    response = client.delete(
        "/activities/Test Activity/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Student is not signed up for this activity"
    }


def test_unregister_rejects_unknown_activity(client):
    # Arrange
    activity = "Unknown"
    email = "student@example.edu"

    # Act
    response = client.delete(
        f"/activities/{activity}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}
