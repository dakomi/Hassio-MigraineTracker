
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from sqlalchemy.orm import Session
from migraine_tracker import crud, models, schemas

@pytest.fixture
def db_session():
    """Fixture for a mock database session."""
    db = MagicMock(spec=Session)
    db.query.return_value.filter.return_value.first.return_value = None
    db.query.return_value.offset.return_value.limit.return_value.all.return_value = []
    return db

@pytest.mark.asyncio
async def test_get_or_create_existing(db_session):
    """Test retrieving an existing item."""
    mock_item = models.Symptom(id=1, name="nausea")
    db_session.query.return_value.filter.return_value.first.return_value = mock_item

    item = await crud.get_or_create(db_session, models.Symptom, "nausea")

    assert item.name == "nausea"
    db_session.add.assert_not_called()

@pytest.mark.asyncio
async def test_get_or_create_new(db_session):
    """Test creating a new item."""
    db_session.query.return_value.filter.return_value.first.return_value = None

    item = await crud.get_or_create(db_session, models.Symptom, "new_symptom")

    assert item.name == "new_symptom"
    db_session.add.assert_called_once()


@pytest.mark.asyncio
@patch("migraine_tracker.crud.home_assistant.get_ha_config", new_callable=AsyncMock)
async def test_get_location_from_ha(mock_get_ha_config, db_session):
    """Test getting location from Home Assistant configuration."""
    mock_get_ha_config.return_value = {"latitude": 51.5072, "longitude": -0.1276}
    lat, lon = await crud.get_location(db_session)
    assert lat == 51.5072
    assert lon == -0.1276

@pytest.mark.asyncio
@patch("migraine_tracker.crud.home_assistant.get_ha_config", new_callable=AsyncMock)
async def test_get_location_default(mock_get_ha_config, db_session):
    """Test falling back to default location."""
    mock_get_ha_config.return_value = {}
    lat, lon = await crud.get_location(db_session)
    assert lat == 40.7128
    assert lon == -74.0060


@pytest.mark.asyncio
@patch("migraine_tracker.crud.get_location", new_callable=AsyncMock)
@patch("migraine_tracker.crud.weather.get_weather_data", new_callable=AsyncMock)
@patch("migraine_tracker.crud.home_assistant.update_ha_sensor", new_callable=AsyncMock)
@patch("migraine_tracker.settings.get_settings")
async def test_create_migraine_event(
    mock_get_settings, mock_update_ha, mock_get_weather, mock_get_loc, db_session
):
    """Test creating a full migraine event."""
    mock_get_settings.return_value = {}
    mock_get_loc.return_value = (40.7128, -74.0060)
    mock_get_weather.return_value = None  # Simulate no weather data for simplicity

    event_data = schemas.MigraineEventCreate(
        start_time=datetime.now(),
        intensity=7,
        notes="A test note",
        pain_location="forehead",
        symptoms=["nausea", "light sensitivity"],
        triggers=["stress"],
    )

    await crud.create_migraine_event_with_weather(db_session, event_data)

    db_session.add.assert_called()
    db_session.commit.assert_called()
    db_session.refresh.assert_called()
    mock_update_ha.assert_called_once()


def test_get_migraine_event(db_session):
    """Test retrieving a single migraine event."""
    mock_event = models.MigraineEvent(
        id=1,
        intensity=5,
        notes="test",
        start_time=datetime.now(),
        pain_location=models.PainLocation(id=1, name="forehead"),
    )
    db_session.query.return_value.filter.return_value.first.return_value = mock_event

    event = crud.get_migraine_event(db_session, 1)

    assert event.id == 1
    assert event.intensity == 5


def test_get_all_migraine_events(db_session):
    """Test retrieving all migraine events."""
    mock_events = [
        models.MigraineEvent(
            id=1,
            intensity=5,
            notes="test1",
            start_time=datetime.now(),
            pain_location=models.PainLocation(id=1, name="forehead"),
        ),
        models.MigraineEvent(
            id=2,
            intensity=8,
            notes="test2",
            start_time=datetime.now(),
            pain_location=models.PainLocation(id=2, name="temple"),
        ),
    ]
    db_session.query.return_value.offset.return_value.limit.return_value.all.return_value = mock_events

    events = crud.get_all_migraine_events(db_session)

    assert len(events) == 2
    assert events[0].id == 1
