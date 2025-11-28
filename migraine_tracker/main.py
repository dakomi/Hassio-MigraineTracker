from fastapi import FastAPI, Depends, HTTPException, File, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Dict
import json
import pandas as pd
import io
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from . import crud, models, schemas, settings, home_assistant, backup
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
scheduler = AsyncIOScheduler()


@app.on_event("startup")
async def startup_event():
    """
    Starts the backup scheduler on application startup.
    """
    app_settings = settings.get_settings()
    backup_interval = app_settings.get("backup_interval", "daily")

    if backup_interval == "daily":
        scheduler.add_job(backup.create_backup, "cron", hour=0)
    elif backup_interval == "weekly":
        scheduler.add_job(backup.create_backup, "cron", day_of_week=0, hour=0)

    if scheduler.get_jobs():
        scheduler.start()


@app.on_event("shutdown")
async def shutdown_event():
    """
    Shuts down the backup scheduler on application shutdown.
    """
    if scheduler.running:
        scheduler.shutdown()


# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/migraines/", response_model=schemas.MigraineEvent)
async def create_migraine(
    migraine: schemas.MigraineEventCreate, db: Session = Depends(get_db)
):
    return await crud.create_migraine_event_with_weather(db=db, migraine_event=migraine)


@app.get("/migraines/", response_model=List[schemas.MigraineEvent])
def read_migraines(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    migraines = crud.get_all_migraine_events(db, skip=skip, limit=limit)
    return migraines


@app.get("/migraines/{migraine_id}", response_model=schemas.MigraineEvent)
def read_migraine(migraine_id: int, db: Session = Depends(get_db)):
    db_migraine = crud.get_migraine_event(db, migraine_event_id=migraine_id)
    if db_migraine is None:
        raise HTTPException(status_code=404, detail="Migraine not found")
    return db_migraine


@app.put("/migraines/{migraine_id}", response_model=schemas.MigraineEvent)
async def update_migraine(
    migraine_id: int,
    migraine: schemas.MigraineEventCreate,
    db: Session = Depends(get_db),
):
    db_migraine = await crud.update_migraine_event_with_weather(
        db, migraine_event_id=migraine_id, migraine_event=migraine
    )
    if db_migraine is None:
        raise HTTPException(status_code=404, detail="Migraine not found")
    return db_migraine


@app.delete("/migraines/{migraine_id}", response_model=schemas.MigraineEvent)
async def delete_migraine(migraine_id: int, db: Session = Depends(get_db)):
    db_migraine = await crud.delete_migraine_event(db, migraine_event_id=migraine_id)
    if db_migraine is None:
        raise HTTPException(status_code=404, detail="Migraine not found")
    return db_migraine


@app.get("/export/", response_class=JSONResponse)
def export_data(db: Session = Depends(get_db)):
    """
    Exports all migraine data to a JSON file.
    """
    migraines = crud.get_all_migraine_events(db)
    migraines_data = [schemas.MigraineEvent.model_validate(m) for m in migraines]
    return JSONResponse(content={"migraines": [m.model_dump_json() for m in migraines_data]})


@app.get("/export/csv", response_class=StreamingResponse)
def export_data_csv(db: Session = Depends(get_db)):
    """
    Exports all migraine data to a CSV file.
    """
    migraines = crud.get_all_migraine_events(db)
    migraines_dict = [
        {
            "start_time": m.start_time,
            "end_time": m.end_time,
            "intensity": m.intensity,
            "notes": m.notes,
            "pain_location": m.pain_location.name,
            "symptoms": ", ".join([s.name for s in m.symptoms]),
            "triggers": ", ".join([t.name for t in m.triggers]),
        }
        for m in migraines
    ]
    df = pd.DataFrame(migraines_dict)
    stream = io.StringIO()
    df.to_csv(stream, index=False)

    response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=migraine_data.csv"
    return response


@app.post("/import/", status_code=201)
async def import_data(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Imports migraine data from a JSON file.
    """
    if file.content_type != "application/json":
        raise HTTPException(status_code=400, detail="Invalid file type")

    contents = await file.read()
    data = json.loads(contents)

    for migraine_data in data.get("migraines", []):
        migraine = schemas.MigraineEventCreate(**migraine_data)
        await crud.create_migraine_event_with_weather(db=db, migraine_event=migraine)
        await asyncio.sleep(1) # Add a 1-second delay between each event to avoid rate limiting

    return {"message": "Data imported successfully"}


@app.get("/preferences/export", response_class=JSONResponse)
def export_preferences(db: Session = Depends(get_db)):
    """
    Exports all user preferences to a JSON file.
    """
    pain_locations = [p.name for p in crud.get_all_pain_locations(db)]
    symptoms = [s.name for s in crud.get_all_symptoms(db)]
    triggers = [t.name for t in crud.get_all_triggers(db)]

    return JSONResponse(content={
        "pain_locations": pain_locations,
        "symptoms": symptoms,
        "triggers": triggers,
    })


@app.post("/preferences/import", status_code=201)
async def import_preferences(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Imports user preferences from a JSON file.
    """
    if file.content_type != "application/json":
        raise HTTPException(status_code=400, detail="Invalid file type")

    contents = await file.read()
    data = json.loads(contents)

    for item in data.get("pain_locations", []):
        crud.get_or_create(db, models.PainLocation, name=item)
    for item in data.get("symptoms", []):
        crud.get_or_create(db, models.Symptom, name=item)
    for item in data.get("triggers", []):
        crud.get_or_create(db, models.Trigger, name=item)

    return {"message": "Preferences imported successfully"}


@app.get("/pain_locations/", response_model=List[schemas.PainLocation])
def read_pain_locations(db: Session = Depends(get_db)):
    return crud.get_all_pain_locations(db)


@app.get("/symptoms/", response_model=List[schemas.Symptom])
def read_symptoms(db: Session = Depends(get_db)):
    return crud.get_all_symptoms(db)


@app.get("/triggers/", response_model=List[schemas.Trigger])
def read_triggers(db: Session = Depends(get_db)):
    return crud.get_all_triggers(db)


@app.get("/settings/", response_model=Dict)
def get_settings():
    return settings.get_settings()


@app.post("/settings/", status_code=204)
def save_settings(new_settings: Dict):
    settings.save_settings(new_settings)
    # Restart the scheduler if the backup interval has changed
    app_settings = settings.get_settings()
    backup_interval = app_settings.get("backup_interval", "daily")

    if scheduler.running:
        scheduler.shutdown()

    if backup_interval == "daily":
        scheduler.add_job(backup.create_backup, "cron", hour=0)
    elif backup_interval == "weekly":
        scheduler.add_job(backup.create_backup, "cron", day_of_week=0, hour=0)

    if scheduler.get_jobs():
        scheduler.start()


@app.get("/ha_entities/", response_model=List)
async def get_ha_entities():
    return await home_assistant.get_ha_entities()
