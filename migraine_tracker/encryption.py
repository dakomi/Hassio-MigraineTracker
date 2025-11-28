import os
from cryptography.fernet import Fernet
from sqlalchemy.types import TypeDecorator, LargeBinary
import base64
import tempfile

# Check if we are in a test environment
IS_TESTING = os.environ.get('TESTING') == 'True'

if IS_TESTING:
    # Use a temporary directory for the key file during testing.
    DATA_DIR = tempfile.gettempdir()
else:
    DATA_DIR = "/data"

KEY_FILE = os.path.join(DATA_DIR, "secret.key")


def load_key():
    """
    Load the encryption key from the KEY_FILE, or generate a new one if it
    doesn't exist.
    """
    # Ensure the data directory exists only when not in testing mode.
    if not IS_TESTING and not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "rb") as f:
            key = f.read()
    else:
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(key)
    return key

# Load the key and initialize Fernet
key = load_key()
fernet = Fernet(key)

class EncryptedString(TypeDecorator):
    """
    A SQLAlchemy TypeDecorator to store strings as encrypted bytes in the database.
    """
    impl = LargeBinary

    def process_bind_param(self, value, dialect):
        if value is not None:
            return fernet.encrypt(value.encode())
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return fernet.decrypt(value).decode()
        return value
