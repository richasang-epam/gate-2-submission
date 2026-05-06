"""
CRM Logger — Step 12 of ETA Agent pipeline. Build and test this FIRST.

Logs every interaction to Salesforce CRM (or in-memory store in mock mode).
Logging failure is not recoverable after the fact — this module must never silently fail.

Required fields per CLAUDE.md:
  inquiry_channel, raw_query, mode, response_text, gps_age_minutes,
  crm_exception_flag, gps_exception_flag, dispute_flag, timestamp_utc
"""

import json
import os
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from typing import Optional
from pathlib import Path

MOCK_MODE = os.getenv("MOCK_MODE", "true").lower() == "true"
_LOG_FILE  = Path(__file__).parent.parent.parent / "mock_data" / "interaction_log.json"

_in_memory_log: list = []    # used when mock mode is active


@dataclass
class CaseEntry:
    case_id: str
    timestamp_utc: str
    inquiry_channel: str
    raw_query: str
    order_id: Optional[str]
    customer_id: Optional[str]
    mode: str
    response_text: str
    gps_age_minutes: Optional[float]
    crm_exception_flag: bool
    gps_exception_flag: bool
    dispute_flag: bool
    escalation_destination: Optional[str]


def log_interaction(
    inquiry_channel: str,
    raw_query: str,
    order_id: Optional[str],
    customer_id: Optional[str],
    mode: str,
    response_text: str,
    gps_age_minutes: Optional[float],
    crm_exception_flag: bool,
    gps_exception_flag: bool,
    dispute_flag: bool,
    escalation_destination: Optional[str] = None,
) -> CaseEntry:

    entry = CaseEntry(
        case_id=_generate_case_id(),
        timestamp_utc=datetime.now(timezone.utc).isoformat(),
        inquiry_channel=inquiry_channel,
        raw_query=raw_query,
        order_id=order_id,
        customer_id=customer_id,
        mode=mode,
        response_text=response_text,
        gps_age_minutes=gps_age_minutes,
        crm_exception_flag=crm_exception_flag,
        gps_exception_flag=gps_exception_flag,
        dispute_flag=dispute_flag,
        escalation_destination=escalation_destination,
    )

    if MOCK_MODE:
        _in_memory_log.append(asdict(entry))
        _persist_mock_log()
    else:
        _write_to_crm(entry)

    return entry


def get_recent_interactions(limit: int = 50) -> list:
    if MOCK_MODE:
        return list(reversed(_in_memory_log))[:limit]
    raise NotImplementedError("Live CRM read not yet implemented — set MOCK_MODE=true")


def _generate_case_id() -> str:
    import random
    return f"CASE-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{random.randint(1000,9999)}"


def _persist_mock_log():
    try:
        _LOG_FILE.write_text(json.dumps(_in_memory_log, indent=2))
    except Exception:
        pass   # best-effort persistence; in-memory log is primary


def _write_to_crm(entry: CaseEntry):
    # TODO: POST to Salesforce REST API
    # POST {SF_INSTANCE_URL}/services/data/v59.0/sobjects/Case/
    # Body: map CaseEntry fields to Salesforce Case object fields
    # Confirm field mappings with Apex IT before implementing
    raise NotImplementedError("Live CRM write not yet implemented — set MOCK_MODE=true")
