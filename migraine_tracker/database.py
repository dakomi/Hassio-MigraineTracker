from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import tempfile

# Check if we are in a test environment
IS_TESTING = os.environ.get('TESTING') == 'True'

if IS_TESTING:
    # During testing, the database URL is typically overridden to use an in-memory DB.
    # We set a temporary path here to avoid creating the /data directory.
    DATA_DIR = tempfile.gettempdir()
else:
    DATA_DIR = "/data"
    # Ensure the data directory exists when not in testing mode.
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

DATABASE_URL = f"sqlite:///{os.path.join(DATA_DIR, 'migraine_tracker.db')}"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
