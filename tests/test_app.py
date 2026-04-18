import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    return TestClient(app, follow_redirects=False)


@pytest.fixture
def reset_activities():
    """Reset activities to original state after each test"""
    original_activities = activities.copy()
    yield
    activities.clear()
    activities.update(original_activities)


def test_root_redirect(client):
    """Test that root endpoint redirects to static index.html"""
    # Arrange - TestClient is set up

    # Act
    response = client.get("/")

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities(client):
    """Test getting all activities"""
    # Arrange - activities are pre-populated in app

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    # Verify structure
    chess_club = data["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)


def test_signup_success(client, reset_activities):
    """Test successful signup for an activity"""
    # Arrange
    activity_name = "Basketball Team"  # starts with empty participants
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert f"Signed up {email} for {activity_name}" == data["message"]
    assert email in activities[activity_name]["participants"]


def test_signup_activity_not_found(client):
    """Test signup for non-existent activity"""
    # Arrange
    activity_name = "NonExistent Activity"
    email = "test@example.com"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" == data["detail"]


def test_signup_already_signed_up(client, reset_activities):
    """Test signup when student is already signed up"""
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # already in participants

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Student already signed up for this activity" == data["detail"]


def test_unregister_success(client, reset_activities):
    """Test successful unregister from an activity"""
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # already signed up

    # Act
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert f"Unregistered {email} from {activity_name}" == data["message"]
    assert email not in activities[activity_name]["participants"]


def test_unregister_activity_not_found(client):
    """Test unregister from non-existent activity"""
    # Arrange
    activity_name = "NonExistent Activity"
    email = "test@example.com"

    # Act
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" == data["detail"]


def test_unregister_not_registered(client, reset_activities):
    """Test unregister when student is not registered"""
    # Arrange
    activity_name = "Chess Club"
    email = "notregistered@example.com"  # not in participants

    # Act
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")

    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Student not registered for this activity" == data["detail"]