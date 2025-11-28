
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime
from migraine_tracker.main import app, get_db
from migraine_tracker import schemas

# Mock database dependency
@pytest.fixture
def override_get_db():
    """Fixture to override the database dependency with a mock."""
    db = MagicMock()
    yield db

def setup_app_dependency_overrides(mock_db):
    """Sets up dependency overrides for the FastAPI app."""
    app.dependency_overrides[get_db] = lambda: mock_db

def teardown_app_dependency_overrides():
    """Clears dependency overrides after tests."""
    app.dependency_overrides = {}

@pytest.fixture
def client(override_get_db):
    """Fixture for the TestClient."""
    with patch("migraine_tracker.main.scheduler"):
        setup_app_dependency_overrides(override_get_db)
        with TestClient(app) as c:
            yield c
        teardown_app_dependency_overrides()


# === Helper for creating mock events ===

def create_mock_event(id, intensity, notes, pain_location_name):
    """Creates a mock event object for testing."""
    event = MagicMock()
    event.id = id
    event.intensity = intensity
    event.notes = notes
    event.start_time = datetime.now()
    event.end_time = None
    # Simulate the nested structure expected by the Pydantic schema
    event.pain_location = MagicMock(spec=schemas.PainLocation)
    event.pain_location.id = id  # Assuming same id for simplicity
    event.pain_location.name = pain_location_name
    event.symptoms = []
    event.triggers = []
    event.weather_data = None
    return event


# === Test Migraine Endpoints ===

@patch("migraine_tracker.crud.create_migraine_event_with_weather", new_callable=AsyncMock)
def test_create_migraine(mock_create, client):
    """Test the POST /migraines/ endpoint."""
    mock_event = create_mock_event(1, 8, "test note", "temple")
    mock_create.return_value = mock_event

    response = client.post(
        "/migraines/",
        json={
            "start_time": datetime.now().isoformat(),
            "intensity": 8,
            "notes": "test note",
            "pain_location": "temple",
            "symptoms": [],
            "triggers": [],
        },
    )
    assert response.status_code == 200
    assert response.json()["intensity"] == 8
    assert response.json()["pain_location"]["name"] == "temple"


@patch("migraine_tracker.crud.get_all_migraine_events")
def test_read_migraines(mock_get_all, client):
    """Test the GET /migraines/ endpoint."""
    mock_get_all.return_value = [create_mock_event(1, 5, "test1", "forehead")]

    response = client.get("/migraines/")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["intensity"] == 5


@patch("migraine_tracker.crud.get_migraine_event")
def test_read_migraine_found(mock_get_one, client):
    """Test GET /migraines/{migraine_id} when found."""
    mock_get_one.return_value = create_mock_event(1, 7, "single", "eye")

    response = client.get("/migraines/1")
    assert response.status_code == 200
    assert response.json()["intensity"] == 7

@patch("migraine_tracker.crud.get_migraine_event")
def test_read_migraine_not_found(mock_get_one, client):
    """Test GET /migraines/{migraine_id} when not found."""
    mock_get_one.return_value = None
    response = client.get("/migraines/999")
    assert response.status_code == 404


# === Test Settings Endpoint ===

@patch("migraine_tracker.settings.get_settings")
def test_get_settings(mock_get, client):
    """Test the GET /settings/ endpoint."""
    mock_get.return_value = {"theme": "dark"}
    response = client.get("/settings/")
    assert response.status_code == 200
    assert response.json() == {"theme": "dark"}

@patch("migraine_tracker.settings.save_settings")
def test_save_settings(mock_save, client):
    """Test the POST /settings/ endpoint."""
    response = client.post("/settings/", json={"theme": "light"})
    assert response.status_code == 204
    mock_save.assert_called_once_with({"theme": "light"})
