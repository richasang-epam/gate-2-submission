"""
Dispute Checker — cross-references APEX_DISPUTES_OPEN daily batch.

The batch is a CSV exported from Aurum at ~02:00 each day (T-1 lag).
Any AI involvement in billing-adjacent data must disclose this lag.
"""

import json
import os
from pathlib import Path

MOCK_MODE = os.getenv("MOCK_MODE", "true").lower() == "true"
_MOCK_FILE = Path(__file__).parent.parent.parent / "mock_data" / "disputes.json"


def has_open_dispute(order_id: str) -> bool:
    if MOCK_MODE:
        return _mock_check(order_id)
    return _batch_check(order_id)


def _mock_check(order_id: str) -> bool:
    try:
        data = json.loads(_MOCK_FILE.read_text())
        return any(d["order_id"] == order_id for d in data)
    except Exception:
        return False    # safe default: don't block escalation on lookup failure


def _batch_check(order_id: str) -> bool:
    # TODO: query the ingested APEX_DISPUTES_OPEN CSV pipeline
    # Pipeline must include schema-change detection (see CLAUDE.md testing requirements)
    # If schema check fails: raise SchemaChangedError — do not silently misread data
    raise NotImplementedError("Live dispute batch check not yet implemented — set MOCK_MODE=true")
