import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


client = TestClient(app)


@pytest.fixture(autouse=True)
def restore_activity_participants():
    original_participants = {
        name: activity["participants"][:]
        for name, activity in activities.items()
    }
    yield
    for name, participants in original_participants.items():
        activities[name]["participants"][:] = participants


def test_unregister_removes_participant():
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    response = client.delete(
        "/activities/Chess%20Club/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    assert email not in activities[activity_name]["participants"]


def test_unregister_returns_not_found_for_unregistered_participant():
    response = client.delete(
        "/activities/Chess%20Club/signup",
        params={"email": "not-signed-up@mergington.edu"},
    )

    assert response.status_code == 404


def test_unregister_returns_not_found_for_unknown_activity():
    response = client.delete(
        "/activities/Unknown/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404


def test_activities_endpoint_returns_fresh_participant_data():
    activity_name = "Art Club"
    email = "new-participant@mergington.edu"
    client.post(
        "/activities/Art%20Club/signup",
        params={"email": email},
    )

    response = client.get("/activities")

    assert response.headers["cache-control"] == "no-store"
    assert email in response.json()[activity_name]["participants"]
