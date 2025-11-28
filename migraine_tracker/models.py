from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Float,
    Text,
    ForeignKey,
    Table,
    Boolean
)
from sqlalchemy.orm import relationship
from .database import Base
from .encryption import EncryptedString

migraine_symptom_association = Table(
    "migraine_symptom_association",
    Base.metadata,
    Column("migraine_event_id", Integer, ForeignKey("migraine_events.id")),
    Column("symptom_id", Integer, ForeignKey("symptoms.id")),
)

migraine_trigger_association = Table(
    "migraine_trigger_association",
    Base.metadata,
    Column("migraine_event_id", Integer, ForeignKey("migraine_events.id")),
    Column("trigger_id", Integer, ForeignKey("triggers.id")),
)


class MigraineEvent(Base):
    __tablename__ = "migraine_events"

    id = Column(Integer, primary_key=True, index=True)
    start_time = Column(DateTime, index=True)
    end_time = Column(DateTime, nullable=True)
    intensity = Column(Integer)
    notes = Column(EncryptedString, nullable=True)  # Encrypted notes

    pain_location_id = Column(Integer, ForeignKey("pain_locations.id"))
    pain_location = relationship("PainLocation")

    symptoms = relationship(
        "Symptom", secondary=migraine_symptom_association, back_populates="migraine_events"
    )
    triggers = relationship(
        "Trigger", secondary=migraine_trigger_association, back_populates="migraine_events"
    )
    weather_data = relationship("WeatherData", uselist=False, back_populates="migraine_event")


class PainLocation(Base):
    __tablename__ = "pain_locations"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(EncryptedString, unique=True, index=True)  # Encrypted name


class Symptom(Base):
    __tablename__ = "symptoms"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(EncryptedString, unique=True, index=True)  # Encrypted name
    migraine_events = relationship(
        "MigraineEvent", secondary=migraine_symptom_association, back_populates="symptoms"
    )


class Trigger(Base):
    __tablename__ = "triggers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(EncryptedString, unique=True, index=True)  # Encrypted name
    migraine_events = relationship(
        "MigraineEvent", secondary=migraine_trigger_association, back_populates="triggers"
    )

class WeatherData(Base):
    __tablename__ = "weather_data"

    id = Column(Integer, primary_key=True, index=True)
    migraine_event_id = Column(Integer, ForeignKey("migraine_events.id"))
    migraine_event = relationship("MigraineEvent", back_populates="weather_data")

    indoor_temp = Column(Float, nullable=True)
    indoor_humidity = Column(Float, nullable=True)
    outdoor_temp = Column(Float, nullable=True)
    outdoor_humidity = Column(Float, nullable=True)
    air_pressure = Column(Float, nullable=True)
    uv_index = Column(Float, nullable=True)
    air_quality = Column(Float, nullable=True)
    pollen_count = Column(Float, nullable=True)
