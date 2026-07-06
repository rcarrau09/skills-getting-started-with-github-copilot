from fastapi.testclient import TestClient

from src.app import app, activities


client = TestClient(app)


def setup_function():
    activities["Chess Club"]["participants"] = ["michael@mergington.edu", "daniel@mergington.edu"]
    activities["Programming Class"]["participants"] = ["emma@mergington.edu", "sophia@mergington.edu"]
    activities["Gym Class"]["participants"] = ["john@mergington.edu", "olivia@mergington.edu"]
    activities["Soccer Team"]["participants"] = ["liam@mergington.edu", "noah@mergington.edu"]
    activities["Basketball Club"]["participants"] = ["ava@mergington.edu", "sophia@mergington.edu"]
    activities["Art Club"]["participants"] = ["mia@mergington.edu", "isabella@mergington.edu"]
    activities["Drama Society"]["participants"] = ["lucas@mergington.edu", "charlotte@mergington.edu"]
    activities["Debate Team"]["participants"] = ["elijah@mergington.edu", "amelia@mergington.edu"]
    activities["Science Club"]["participants"] = ["benjamin@mergington.edu", "harper@mergington.edu"]


def test_root_redirects_to_static_index_page():
    # Arrange

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code in (307, 308)
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_all_activities_with_expected_fields():
    # Arrange

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 9
    assert "Chess Club" in payload

    for activity in payload.values():
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)


def test_signup_for_activity_adds_participant_and_returns_message():
    # Arrange
    email = "newstudent@mergington.edu"

    # Act
    response = client.post("/activities/Chess Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert email in activities["Chess Club"]["participants"]
    assert response.json()["message"] == f"Signed up {email} for Chess Club"


def test_signup_for_activity_rejects_duplicate_email_without_mutating_participants():
    # Arrange
    participants_before = list(activities["Chess Club"]["participants"])

    # Act
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "michael@mergington.edu"},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"
    assert activities["Chess Club"]["participants"] == participants_before


def test_signup_for_activity_returns_404_for_unknown_activity_without_mutating_existing_data():
    # Arrange
    participants_before = list(activities["Chess Club"]["participants"])

    # Act
    response = client.post(
        "/activities/Unknown Club/signup",
        params={"email": "newstudent@mergington.edu"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
    assert activities["Chess Club"]["participants"] == participants_before


def test_signup_for_activity_with_empty_email_matches_current_behavior():
    # Arrange

    # Act
    response = client.post("/activities/Chess Club/signup", params={"email": ""})

    # Assert
    assert response.status_code == 200
    assert "" in activities["Chess Club"]["participants"]


def test_signup_for_activity_with_spaces_in_activity_name_path_works():
    # Arrange
    email = "anotherstudent@mergington.edu"

    # Act
    response = client.post("/activities/Programming Class/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert email in activities["Programming Class"]["participants"]


def test_unregister_participant_returns_404_for_unknown_activity():
    # Arrange
    participants_before = list(activities["Chess Club"]["participants"])

    # Act
    response = client.delete("/activities/Unknown Club/participants/michael@mergington.edu")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
    assert activities["Chess Club"]["participants"] == participants_before


def test_unregister_participant_returns_404_for_unknown_participant():
    # Arrange
    participants_before = list(activities["Chess Club"]["participants"])

    # Act
    response = client.delete("/activities/Chess Club/participants/notfound@mergington.edu")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
    assert activities["Chess Club"]["participants"] == participants_before


def test_unregister_participant_removes_their_email():
    # Arrange

    # Act
    response = client.delete("/activities/Chess Club/participants/michael@mergington.edu")

    # Assert
    assert response.status_code == 200
    assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]
    assert response.json()["message"] == "Unregistered michael@mergington.edu from Chess Club"
