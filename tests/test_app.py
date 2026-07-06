from fastapi.testclient import TestClient

from src.app import app, activities


client = TestClient(app)


def setup_function():
    activities["Chess Club"]["participants"] = ["michael@mergington.edu", "daniel@mergington.edu"]


def test_unregister_participant_removes_their_email():
    response = client.delete("/activities/Chess Club/participants/michael@mergington.edu")

    assert response.status_code == 200
    assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]
    assert response.json()["message"] == "Unregistered michael@mergington.edu from Chess Club"
