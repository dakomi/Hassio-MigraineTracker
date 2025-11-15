import os
import httpx
from typing import List
from datetime import datetime
from . import models

# Get the Supervisor token from the environment variables
SUPERVISOR_TOKEN = os.environ.get("SUPERVISOR_TOKEN")
HA_API_URL = "http://supervisor/core/api"


async def get_ha_config():
    """
    Fetches the Home Assistant configuration.
    """
    if not SUPERVISOR_TOKEN:
        print("SUPERVISOR_TOKEN not found. Cannot fetch HA config.")
        return None

    headers = {
        "Authorization": f"Bearer {SUPERVISOR_TOKEN}",
        "Content-Type": "application/json",
    }

    url = f"{HA_API_URL}/config"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"Failed to fetch HA config. Status code: {e.response.status_code}")
            return None
        except httpx.RequestError as e:
            print(f"An error occurred while requesting {e.request.url!r}.")
            return None


async def get_ha_entities():
    """
    Fetches a list of all Home Assistant entities.
    """
    if not SUPERVISOR_TOKEN:
        print("SUPERVISOR_TOKEN not found. Cannot fetch HA entities.")
        return []

    headers = {
        "Authorization": f"Bearer {SUPERVISOR_TOKEN}",
        "Content-Type": "application/json",
    }

    url = f"{HA_API_URL}/states"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"Failed to fetch HA entities. Status code: {e.response.status_code}")
            return []
        except httpx.RequestError as e:
            print(f"An error occurred while requesting {e.request.url!r}.")
            return []


async def get_ha_entity_state(entity_id: str):
    """
    Fetches the state of a specific Home Assistant entity.
    """
    if not SUPERVISOR_TOKEN:
        print("SUPERVISOR_TOKEN not found. Cannot fetch HA entity state.")
        return None

    headers = {
        "Authorization": f"Bearer {SUPERVISOR_TOKEN}",
        "Content-Type": "application/json",
    }

    url = f"{HA_API_URL}/states/{entity_id}"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"Failed to fetch HA entity state for {entity_id}. Status code: {e.response.status_code}")
            return None
        except httpx.RequestError as e:
            print(f"An error occurred while requesting {e.request.url!r}.")
            return None


async def update_ha_sensor(migraines: List[models.MigraineEvent]):
    """
    Updates the Home Assistant sensor with the current migraine status.
    """
    if not SUPERVISOR_TOKEN:
        print("SUPERVISOR_TOKEN not found. Skipping Home Assistant sensor update.")
        return

    headers = {
        "Authorization": f"Bearer {SUPERVISOR_TOKEN}",
        "Content-Type": "application/json",
    }

    entity_id = "sensor.migraine_current_status"

    # Determine the current status based on active migraines
    active_migraines = [
        m for m in migraines if m.end_time is None or m.end_time > datetime.now()
    ]

    if active_migraines:
        active_count = len(active_migraines)
        avg_severity = sum(m.intensity for m in active_migraines) / active_count
        earliest_start_time = min(m.start_time for m in active_migraines)

        state = "on"  # Use 'on' for boolean true in HA sensors
        attributes = {
            "friendly_name": "Current Migraine Status",
            "active_count": active_count,
            "severity": round(avg_severity, 2),
            "start_time": earliest_start_time.isoformat(),
        }
    else:
        state = "off" # Use 'off' for boolean false
        attributes = {
            "friendly_name": "Current Migraine Status",
            "active_count": 0,
        }

    payload = {"state": state, "attributes": attributes}

    url = f"{HA_API_URL}/states/{entity_id}"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            print(f"Successfully updated Home Assistant sensor: {entity_id}")
        except httpx.HTTPStatusError as e:
            print(f"Failed to update Home Assistant sensor. Status code: {e.response.status_code}")
            print(f"Response: {e.response.text}")
        except httpx.RequestError as e:
            print(f"An error occurred while requesting {e.request.url!r}.")
