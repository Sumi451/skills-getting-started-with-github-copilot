from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)


def setup_function():
    # reset in-memory activities to known state for each test
    activities.clear()
    activities.update({
        "Test Club": {
            "description": "A test activity",
            "schedule": "Now",
            "max_participants": 5,
            "participants": ["alice@example.com"]
        }
    })


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert "Test Club" in data


def test_signup_success():
    resp = client.post("/activities/Test%20Club/signup?email=bob%40example.com")
    assert resp.status_code == 200
    assert resp.json()["message"] == "Signed up bob@example.com for Test Club"
    assert "bob@example.com" in activities["Test Club"]["participants"]


def test_signup_duplicate():
    # alice is already signed up in setup
    resp = client.post("/activities/Test%20Club/signup?email=alice%40example.com")
    assert resp.status_code == 400


def test_unregister_success():
    resp = client.delete("/activities/Test%20Club/participants?email=alice%40example.com")
    assert resp.status_code == 200
    assert resp.json()["message"] == "Unregistered alice@example.com from Test Club"
    assert "alice@example.com" not in activities["Test Club"]["participants"]


def test_unregister_not_signed_up():
    resp = client.delete("/activities/Test%20Club/participants?email=charlie%40example.com")
    assert resp.status_code == 400


def test_activity_not_found():
    resp = client.delete("/activities/Nope%20Club/participants?email=alice%40example.com")
    assert resp.status_code == 404
