import copy
import pytest
import ACEest_Fitness
from ACEest_Fitness import app, clients_db, workouts_db


@pytest.fixture(autouse=True)
def reset_state():
    orig_clients = copy.deepcopy(clients_db)
    orig_workouts = copy.deepcopy(workouts_db)
    yield
    clients_db[:] = orig_clients
    workouts_db[:] = orig_workouts


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


def test_health_endpoint(client):
    res = client.get("/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "UP"
    assert data["service"] == "ACEest Fitness & Gym"


def test_version_endpoint(client):
    res = client.get("/version")
    assert res.status_code == 200
    assert res.get_json()["version"] == ACEest_Fitness.APP_VERSION


def test_home_dashboard(client):
    res = client.get("/")
    assert res.status_code == 200
    html = res.get_data(as_text=True)
    assert "ACEest Fitness & Gym" in html
    assert "Aarav Sharma" in html


def test_get_and_create_client(client):
    res = client.get("/clients")
    assert res.status_code == 200
    assert len(res.get_json()["clients"]) == 1

    post_res = client.post(
        "/clients",
        json={"name": "Meera Nair", "program": "Fat Loss", "adherence": 90},
    )
    assert post_res.status_code == 201
    created = post_res.get_json()
    assert created["name"] == "Meera Nair"
    assert created["program"] == "Fat Loss"

    missing_res = client.post("/clients", json={"program": "Beginner"})
    assert missing_res.status_code == 400


def test_generate_program(client):
    res = client.post(
        "/programs/generate",
        json={"client_name": "Aarav Sharma", "goal": "Fat Loss"},
    )
    assert res.status_code == 200
    data = res.get_json()
    assert data["goal"] == "Fat Loss"
    assert data["program"] in ACEest_Fitness.PROGRAM_TEMPLATES["Fat Loss"]

    bad_res = client.post("/programs/generate", json={})
    assert bad_res.status_code == 400


def test_get_and_log_workout(client):
    res = client.post(
        "/workouts",
        json={
            "client_name": "Aarav Sharma",
            "workout_type": "Cardio",
            "duration_min": 45,
            "notes": "Zone 2 run",
        },
    )
    assert res.status_code == 201
    assert res.get_json()["workout_type"] == "Cardio"

    list_res = client.get("/workouts")
    assert list_res.status_code == 200
    assert len(list_res.get_json()["workouts"]) == 2
