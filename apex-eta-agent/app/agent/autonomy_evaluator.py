"""
Autonomy Evaluator — Step 9 of ETA Agent pipeline.

Applies the rules from CLAUDE.md to determine which mode the agent operates in.

Modes:
  AUTONOMOUS          — respond with best-estimate ETA window
  SUPERVISED          — respond with widened window + staleness disclosure; flag for review
  ESCALATE_DISPATCHER — route to dispatcher (GPS stale / Driver App offline)
  ESCALATE_HUMAN      — route to human agent (exception, dispute, frustration, not found)

Rule precedence (first match wins):
  1. Order not found                       → ESCALATE_HUMAN
  2. GPS unavailable / Driver App offline  → ESCALATE_DISPATCHER
  3. Any exception flag set (CRM or GPS)   → ESCALATE_HUMAN (exception handler)
  4. Open dispute in APEX_DISPUTES_OPEN    → ESCALATE_HUMAN
  5. Delivery complete, no scan event      → ESCALATE_HUMAN (potential missing parcel)
  6. GPS stale (> 60 min)                  → ESCALATE_DISPATCHER
  7. GPS degraded (30–60 min)              → SUPERVISED
  8. Strategic account (ACCT_MGR set)      → ESCALATE_HUMAN (named-queue routing)
  9. GPS fresh (< 30 min), no flags       → AUTONOMOUS
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from app.agent.order_resolver import OrderLookupResult
from app.agent.gps_interpreter import GPSResult


class Mode(str, Enum):
    AUTONOMOUS          = "autonomous"
    SUPERVISED          = "supervised"
    ESCALATE_DISPATCHER = "escalate_dispatcher"
    ESCALATE_HUMAN      = "escalate_human"


@dataclass
class EvaluationResult:
    mode: Mode
    reason: str
    gps_age_minutes: Optional[float]
    crm_exception: bool
    gps_exception: bool
    open_dispute: bool
    strategic_account: bool


def evaluate(
    order_result: OrderLookupResult,
    gps_result: GPSResult,
    open_dispute: bool,
) -> EvaluationResult:

    base = dict(
        gps_age_minutes=gps_result.reading.ping_age_minutes if gps_result.reading else None,
        crm_exception=order_result.order.exception_status if order_result.order else False,
        gps_exception=gps_result.reading.exception_flag if gps_result.reading else False,
        open_dispute=open_dispute,
        strategic_account=bool(order_result.order.acct_mgr) if order_result.order else False,
    )

    # Rule 1
    if not order_result.found:
        return EvaluationResult(mode=Mode.ESCALATE_HUMAN,
                                reason="Order not found after primary and secondary lookup",
                                **base)

    # Rule 2
    if not gps_result.available:
        return EvaluationResult(mode=Mode.ESCALATE_DISPATCHER,
                                reason="Driver App GPS unavailable or API unreachable",
                                **base)

    order = order_result.order
    reading = gps_result.reading

    # Rule 3 — CRM exception flag
    if order.exception_status:
        return EvaluationResult(mode=Mode.ESCALATE_HUMAN,
                                reason="CRM exception flag set on delivery record",
                                **base)

    # Rule 3 — GPS exception flag
    if reading.exception_flag:
        return EvaluationResult(mode=Mode.ESCALATE_HUMAN,
                                reason="Driver App exception flag set",
                                **base)

    # Rule 4
    if open_dispute:
        return EvaluationResult(mode=Mode.ESCALATE_HUMAN,
                                reason="Open dispute found in APEX_DISPUTES_OPEN for this order",
                                **base)

    # Rule 5 — delivery complete but no scan event
    if order.status == "delivered_no_scan":
        return EvaluationResult(mode=Mode.ESCALATE_HUMAN,
                                reason="Delivery marked complete but no scan-on-delivery event — potential missing parcel",
                                **base)

    # Rule 6
    if gps_result.staleness_label == "stale":
        return EvaluationResult(mode=Mode.ESCALATE_DISPATCHER,
                                reason=f"GPS ping is {reading.ping_age_minutes:.0f} min old (threshold: 60 min)",
                                **base)

    # Rule 7
    if gps_result.staleness_label == "degraded":
        return EvaluationResult(mode=Mode.SUPERVISED,
                                reason=f"GPS ping is {reading.ping_age_minutes:.0f} min old — widened window, flagged for review",
                                **base)

    # Rule 8 — strategic account (ACCT_MGR field set); uniform agent responses carry reputational risk
    if order.acct_mgr:
        return EvaluationResult(mode=Mode.ESCALATE_HUMAN,
                                reason=f"Strategic account — ACCT_MGR {order.acct_mgr} assigned; routing to named agent queue",
                                **base)

    # Rule 9
    return EvaluationResult(mode=Mode.AUTONOMOUS,
                            reason=f"GPS fresh ({reading.ping_age_minutes:.0f} min), no flags",
                            **base)
