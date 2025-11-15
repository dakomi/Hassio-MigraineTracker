import shutil
from datetime import datetime
import os

DATA_DIR = "/data"
DB_FILE = os.path.join(DATA_DIR, "migraine_tracker.db")
BACKUP_DIR = os.path.join(DATA_DIR, "backups")

def create_backup():
    """
    Creates a timestamped backup of the database file.
    """
    if not os.path.exists(DB_FILE):
        print("Database file not found. Skipping backup.")
        return

    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_file = os.path.join(BACKUP_DIR, f"migraine_tracker_{timestamp}.db")

    try:
        shutil.copy(DB_FILE, backup_file)
        print(f"Successfully created backup: {backup_file}")
    except Exception as e:
        print(f"Failed to create backup: {e}")
