from sqlalchemy.orm import Session
from . import models, schemas, weather, home_assistant, settings
from datetime import datetime, timedelta
import asyncio

async def get_location(db: Session):
    """
    Gets the user's location from the Home Assistant config.
    Falls back to a default location if the config is not available.
    """
    ha_config = await home_assistant.get_ha_config()
    if ha_config and "latitude" in ha_config and "longitude" in ha_config:
        return ha_config["latitude"], ha_config["longitude"]
    else:
        # Default to New York City if location is not available
        return 40.7128, -74.0060

async def get_or_create(db: Session, model, name: str):
    """
    Helper function to get an existing object or create a new one if it
    doesn't exist.
    """
    instance = await asyncio.to_thread(db.query(model).filter(model.name == name).first)
    if instance:
        return instance
    else:
        instance = model(name=name)
        db.add(instance)
        return instance


async def create_migraine_event_with_weather(db: Session, migraine_event: schemas.MigraineEventCreate):
    """
    Create a new migraine event and fetch the associated weather data.
    """
    app_settings = settings.get_settings()
    latitude, longitude = await get_location(db)

    pain_location = await get_or_create(db, models.PainLocation, name=migraine_event.pain_location)

    symptoms = [await get_or_create(db, models.Symptom, name=symptom) for symptom in migraine_event.symptoms]
    triggers = [await get_or_create(db, models.Trigger, name=trigger) for trigger in migraine_event.triggers]

    db_migraine_event = models.MigraineEvent(
        start_time=migraine_event.start_time,
        end_time=migraine_event.end_time,
        intensity=migraine_event.intensity,
        notes=migraine_event.notes,
        pain_location=pain_location,
        symptoms=symptoms,
        triggers=triggers,
    )
    db.add(db_migraine_event)
    await asyncio.to_thread(db.commit)
    await asyncio.to_thread(db.refresh, db_migraine_event)

    # Fetch and store weather data
    start_fetch = db_migraine_event.start_time - timedelta(hours=app_settings.get("fetch_range_before", 3))
    end_fetch = (db_migraine_event.end_time or datetime.now()) + timedelta(hours=app_settings.get("fetch_range_after", 1))

    weather_data = await weather.get_weather_data(
        latitude, longitude, start_fetch, end_fetch
    )

    # Fetch indoor sensor data
    indoor_temp = None
    if app_settings.get("indoor_temp_sensor"):
        state = await home_assistant.get_ha_entity_state(app_settings["indoor_temp_sensor"])
        if state and "state" in state:
            indoor_temp = float(state["state"])

    indoor_humidity = None
    if app_settings.get("indoor_humidity_sensor"):
        state = await home_assistant.get_ha_entity_state(app_settings["indoor_humidity_sensor"])
        if state and "state" in state:
            indoor_humidity = float(state["state"])

    if weather_data:
        db_weather_data = models.WeatherData(
            migraine_event_id=db_migraine_event.id,
            indoor_temp=indoor_temp,
            indoor_humidity=indoor_humidity,
            outdoor_temp=weather_data.temperature,
            outdoor_humidity=weather_data.humidity,
            air_pressure=weather_data.pressure,
            uv_index=weather_data.uv_index,
            air_quality=weather_data.air_quality,
            pollen_count=weather_data.pollen_count,
        )
        db.add(db_weather_data)
        await asyncio.to_thread(db.commit)
        await asyncio.to_thread(db.refresh, db_weather_data)

    # Update Home Assistant sensor
    all_migraines = get_all_migraine_events(db)
    await home_assistant.update_ha_sensor(all_migraines)

    return db_migraine_event


def get_migraine_event(db: Session, migraine_event_id: int):
    """
    Get a single migraine event by its ID.
    """
    return (
        db.query(models.MigraineEvent)
        .filter(models.MigraineEvent.id == migraine_event_id)
        .first()
    )


def get_all_migraine_events(db: Session, skip: int = 0, limit: int = 100):
    """
    Get all migraine events, with optional pagination.
    """
    return db.query(models.MigraineEvent).offset(skip).limit(limit).all()


async def update_migraine_event_with_weather(
    db: Session, migraine_event_id: int, migraine_event: schemas.MigraineEventCreate
):
    """
    Update an existing migraine event and re-fetch weather data if necessary.
    """
    app_settings = settings.get_settings()
    latitude, longitude = await get_location(db)

    db_migraine_event = get_migraine_event(db, migraine_event_id)
    if not db_migraine_event:
        return None

    # Check if the start or end time has changed
    time_changed = (
        db_migraine_event.start_time != migraine_event.start_time
        or db_migraine_event.end_time != migraine_event.end_time
    )

    # Update the simple fields
    db_migraine_event.start_time = migraine_event.start_time
    db_migraine_event.end_time = migraine_event.end_time
    db_migraine_event.intensity = migraine_event.intensity
    db_migraine_event.notes = migraine_event.notes

    # Update the relationships
    db_migraine_event.pain_location = await get_or_create(
        db, models.PainLocation, name=migraine_event.pain_location
    )
    db_migraine_event.symptoms = [
        await get_or_create(db, models.Symptom, name=symptom)
        for symptom in migraine_event.symptoms
    ]
    db_migraine_event.triggers = [
        await get_or_create(db, models.Trigger, name=trigger)
        for trigger in migraine_event.triggers
    ]

    await asyncio.to_thread(db.commit)
    await asyncio.to_thread(db.refresh, db_migraine_event)

    # Re-fetch weather data if the time has changed
    if time_changed:
        start_fetch = db_migraine_event.start_time - timedelta(hours=app_settings.get("fetch_range_before", 3))
        end_fetch = (db_migraine_event.end_time or datetime.now()) + timedelta(hours=app_settings.get("fetch_range_after", 1))

        weather_data = await weather.get_weather_data(
            latitude, longitude, start_fetch, end_fetch
        )

        # Fetch indoor sensor data
        indoor_temp = None
        if app_settings.get("indoor_temp_sensor"):
            state = await home_assistant.get_ha_entity_state(app_settings["indoor_temp_sensor"])
            if state and "state" in state:
                indoor_temp = float(state["state"])

        indoor_humidity = None
        if app_settings.get("indoor_humidity_sensor"):
            state = await home_assistant.get_ha_entity_state(app_settings["indoor_humidity_sensor"])
            if state and "state" in state:
                indoor_humidity = float(state["state"])

        if weather_data:
            db_weather = db.query(models.WeatherData).filter_by(migraine_event_id=db_migraine_event.id).first()
            if db_weather:
                db_weather.indoor_temp = indoor_temp
                db_weather.indoor_humidity = indoor_humidity
                db_weather.outdoor_temp = weather_data.temperature
                db_weather.outdoor_humidity = weather_data.humidity
                db_weather.air_pressure = weather_data.pressure
                db_weather.uv_index = weather_data.uv_index
                db_weather.air_quality = weather_data.air_quality
                db_weather.pollen_count = weather_data.pollen_count
            else:
                db_weather = models.WeatherData(
                    migraine_event_id=db_migraine_event.id,
                    indoor_temp=indoor_temp,
                    indoor_humidity=indoor_humidity,
                    outdoor_temp=weather_data.temperature,
                    outdoor_humidity=weather_data.humidity,
                    air_pressure=weather_data.pressure,
                    uv_index=weather_data.uv_index,
                    air_quality=weather_data.air_quality,
                    pollen_count=weather_data.pollen_count,
                )
                db.add(db_weather)

            await asyncio.to_thread(db.commit)
            await asyncio.to_thread(db.refresh, db_weather)

    # Update Home Assistant sensor
    all_migraines = get_all_migraine_events(db)
    await home_assistant.update_ha_sensor(all_migraines)

    return db_migraine_event


async def delete_migraine_event(db: Session, migraine_event_id: int):
    """
    Delete a migraine event and update the Home Assistant sensor.
    """
    db_migraine_event = get_migraine_event(db, migraine_event_id)

    if db_migraine_event:
        await asyncio.to_thread(db.delete, db_migraine_event)
        await asyncio.to_thread(db.commit)

    # Update Home Assistant sensor regardless of whether an event was deleted
    all_migraines = get_all_migraine_events(db)
    await home_assistant.update_ha_sensor(all_migraines)

    return db_migraine_event

def get_all_pain_locations(db: Session):
    return db.query(models.PainLocation).all()

def get_all_symptoms(db: Session):
    return db.query(models.Symptom).all()

def get_all_triggers(db: Session):
    return db.query(models.Trigger).all()
