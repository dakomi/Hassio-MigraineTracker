from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional


class PainLocationBase(BaseModel):
    name: str


class PainLocationCreate(PainLocationBase):
    pass


class PainLocation(PainLocationBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class SymptomBase(BaseModel):
    name: str


class SymptomCreate(SymptomBase):
    pass


class Symptom(SymptomBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class TriggerBase(BaseModel):
    name: str


class TriggerCreate(TriggerBase):
    pass


class Trigger(TriggerBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class WeatherDataBase(BaseModel):
    indoor_temp: Optional[float] = None
    indoor_humidity: Optional[float] = None
    outdoor_temp: Optional[float] = None
    outdoor_humidity: Optional[float] = None
    air_pressure: Optional[float] = None
    uv_index: Optional[float] = None
    air_quality: Optional[float] = None
    pollen_count: Optional[float] = None

class WeatherDataCreate(WeatherDataBase):
    pass

class WeatherData(WeatherDataBase):
    id: int
    migraine_event_id: int
    model_config = ConfigDict(from_attributes=True)

# Schema for creating a migraine event (input)
class MigraineEventBase(BaseModel):
    start_time: datetime
    end_time: Optional[datetime] = None
    intensity: int
    notes: Optional[str] = None
    pain_location: str  # Simplified to a string
    symptoms: List[str]   # Simplified to a list of strings
    triggers: List[str]   # Simplified to a list of strings


class MigraineEventCreate(MigraineEventBase):
    pass

# Schema for reading a migraine event (output)
class MigraineEvent(BaseModel):
    id: int
    start_time: datetime
    end_time: Optional[datetime] = None
    intensity: int
    notes: Optional[str] = None
    pain_location: PainLocation
    symptoms: List[Symptom] = []
    triggers: List[Trigger] = []
    weather_data: Optional[WeatherData] = None

    model_config = ConfigDict(from_attributes=True)
