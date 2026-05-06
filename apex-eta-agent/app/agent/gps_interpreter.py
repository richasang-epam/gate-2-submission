"""
GPS Interpreter — Steps 5–8 of ETA Agent pipeline.

Retrieves the driver's last GPS ping and computes staleness in minutes.

BLOCKED: Driver App backend API is not yet confirmed (see D6 Q1 / CLAUDE.md).
In MOCK_MODE=true, reads from mock_data/gps_positions.json.

Do NOT begin live GPS integration until Driver App team confirms the API spec.
Do NOT extrapolate position from a stale ping.
"""

import json
import os
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

MOCK_MODE = os.getenv("MOCK_MODE", "true").lower() == "true"
_MOCK_FILE = Path(__file__).parent.parent.parent / "mock_data" / "gps_positions.json"

# Staleness thresholds from CLAUDE.md — do not change without design review
THRESHOLD_AUTONOMOUS_MINUTES = 30
THRESHOLD_SUPERVISED_MINUTES  = 60


@dataclass
class GPSReading:
    driver_id: str
    lat: float
    lon: float
    ping_age_minutes: float
    exception_flag: bool          # Driver App exception flag (Y/N)
    api_available: bool = True


@dataclass
class GPSResult:
    available: bool
    reading: Optional[GPSReading]
    staleness_label: str          # "fresh" | "degraded" | "stale" | "unavailable"
    error: Optional[str] = None


def get_gps(driver_id: str) -> GPSResult:
    if MOCK_MODE:
        return _mock_gps(driver_id)
    return _live_gps(driver_id)


def _mock_gps(driver_id: str) -> GPSResult:
    try:
        data = json.loads(_MOCK_FILE.read_text())
    except Exception as e:
        return GPSResult(available=False, reading=None,
                         staleness_label="unavailable", error=str(e))

    entry = next((d for d in data if d["driver_id"] == driver_id), None)
    if not entry:
        return GPSResult(available=False, reading=None,
                         staleness_label="unavailable",
                         error=f"No GPS record for driver {driver_id}")

    age = entry["ping_age_minutes"]
    reading = GPSReading(
        driver_id=driver_id,
        lat=entry["lat"],
        lon=entry["lon"],
        ping_age_minutes=age,
        exception_flag=entry.get("exception_flag", False),
    )
    return GPSResult(available=True, reading=reading,
                     staleness_label=_label(age))


def _label(age_minutes: float) -> str:
    if age_minutes < THRESHOLD_AUTONOMOUS_MINUTES:
        return "fresh"
    if age_minutes < THRESHOLD_SUPERVISED_MINUTES:
        return "degraded"
    return "stale"


def _live_gps(driver_id: str) -> GPSResult:
    # TODO: implement once Driver App team confirms API spec (D6 Q1)
    # Likely: GET {DRIVER_APP_BASE_URL}/api/v1/drivers/{driver_id}/location
    # Headers: Authorization: Bearer {DRIVER_APP_API_KEY}
    # Response shape: { lat, lon, timestamp_utc, exception_flag }
    # Compute ping_age_minutes from (now_utc - timestamp_utc).total_seconds() / 60
    raise NotImplementedError(
        "GPS API not confirmed — blocked per CLAUDE.md. Set MOCK_MODE=true."
    )
