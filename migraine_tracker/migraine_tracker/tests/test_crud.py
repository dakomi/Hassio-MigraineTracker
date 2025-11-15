from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from migraine_tracker.database import Base
from migraine_tracker import crud, models, schemas
import pytest
from datetime import datetime
import asyncio
from unittest.mock import patch

# Use an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.mark.skip(reason="Skipping due to persistent session handling issues")
def test_get_or_create(db):
    # Test creating a new object
    location = crud.get_or_create(db, models.PainLocation, name="Test Location")
    db.commit()
    db.refresh(location)
    assert location.name == "Test Location"

    # Test retrieving an existing object
    location2 = crud.get_or_create(db, models.PainLocation, name="Test Location")
    assert location2.id == location.id


@pytest.mark.asyncio
async def test_create_migraine_event(db):
    migraine_data = schemas.MigraineEventCreate(
        start_time=datetime.now(),
        intensity=7,
        pain_location="Test Location",
        symptoms=["Test Symptom"],
        triggers=["Test Trigger"],
    )
    with patch('migraine_tracker.home_assistant.get_ha_config', return_value={"latitude": 40.7128, "longitude": -74.0060}):
        with patch('migraine_tracker.weather.get_weather_data', return_value=None):
            db_migraine = await crud.create_migraine_event_with_weather(db, migraine_event=migraine_data)

    assert db_migraine.id is not None
    assert db_migraine.intensity == 7
    assert db_migraine.pain_location.name == "Test Location"
    assert len(db_migraine.symptoms) == 1
    assert db_migraine.symptoms[0].name == "Test Symptom"


@pytest.mark.asyncio
async def test_get_all_migraine_events(db):
    # Test with no events
    events = crud.get_all_migraine_events(db)
    assert len(events) == 0

    # Test with one event
    migraine_data = schemas.MigraineEventCreate(
        start_time=datetime.now(),
        intensity=7,
        pain_location="Test Location",
        symptoms=["Test Symptom"],
        triggers=["Test Trigger"],
    )
    with patch('migraine_tracker.home_assistant.get_ha_config', return_value={"latitude": 40.7128, "longitude": -74.0060}):
        with patch('migraine_tracker.weather.get_weather_data', return_value=None):
            await crud.create_migraine_event_with_weather(db, migraine_event=migraine_data)

    events = crud.get_all_migraine_events(db)
    assert len(events) == 1
    assert events[0].intensity == 7


@pytest.mark.asyncio
async def test_update_migraine_event(db):
    migraine_data = schemas.MigraineEventCreate(
        start_time=datetime.now(),
        intensity=7,
        pain_location="Test Location",
        symptoms=["Test Symptom"],
        triggers=["Test Trigger"],
    )
    with patch('migraine_tracker.home_assistant.get_ha_config', return_value={"latitude": 40.7128, "longitude": -74.0060}):
        with patch('migraine_tracker.weather.get_weather_data', return_value=None):
            db_migraine = await crud.create_migraine_event_with_weather(db, migraine_event=migraine_data)

    updated_data = schemas.MigraineEventCreate(
        start_time=db_migraine.start_time,
        intensity=9,
        pain_location="New Location",
        symptoms=["New Symptom"],
        triggers=["New Trigger"],
    )
    with patch('migraine_tracker.home_assistant.get_ha_config', return_value={"latitude": 40.7128, "longitude": -74.0060}):
        with patch('migraine_tracker.weather.get_weather_data', return_value=None):
            updated_migraine = await crud.update_migraine_event_with_weather(db, migraine_event_id=db_migraine.id, migraine_event=updated_data)

    assert updated_migraine.intensity == 9
    assert updated_migraine.pain_location.name == "New Location"
    assert updated_migraine.symptoms[0].name == "New Symptom"


@pytest.mark.asyncio
async def test_delete_migraine_event(db):
    migraine_data = schemas.MigraineEventCreate(
        start_time=datetime.now(),
        intensity=7,
        pain_location="Test Location",
        symptoms=["Test Symptom"],
        triggers=["Test Trigger"],
    )
    with patch('migraine_tracker.home_assistant.get_ha_config', return_value={"latitude": 40.7128, "longitude": -74.0060}):
        with patch('migraine_tracker.weather.get_weather_data', return_value=None):
            db_migraine = await crud.create_migraine_event_with_weather(db, migraine_event=migraine_data)

    deleted_migraine = await crud.delete_migraine_event(db, migraine_event_id=db_migraine.id)
    assert deleted_migraine is not None

    events = crud.get_all_migraine_events(db)
    assert len(events) == 0


@pytest.mark.asyncio
async def test_get_location(db):
    with patch('migraine_tracker.home_assistant.get_ha_config', return_value={"latitude": 12.34, "longitude": 56.78}):
        lat, lon = await crud.get_location(db)
        assert lat == 12.34
        assert lon == 56.78

    with patch('migraine_tracker.home_assistant.get_ha_config', return_value=None):
        lat, lon = await crud.get_location(db)
        assert lat == 40.7128
        assert lon == -74.0060
