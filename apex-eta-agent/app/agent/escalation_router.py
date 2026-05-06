"""
Escalation Router — Step 11 of ETA Agent pipeline.

Builds escalation payloads and customer-facing acknowledgement messages.
Every escalation path must be tested before ship (see CLAUDE.md testing requirements).
"""

from dataclasses import dataclass
from app.agent.autonomy_evaluator import EvaluationResult, Mode
from app.agent.order_resolver import Order
from typing import Optional


@dataclass
class EscalationPayload:
    destination: str             # "dispatcher" | "exception_handler" | "human_agent" | "billing"
    priority: str                # "normal" | "high" | "urgent"
    order_id: Optional[str]
    customer_name: Optional[str]
    reason: str
    gps_age_minutes: Optional[float]
    crm_exception: bool
    gps_exception: bool
    open_dispute: bool
    customer_message: str        # what to send to the customer


def route_escalation(order: Optional[Order],
                     eval_result: EvaluationResult,
                     channel: str) -> EscalationPayload:

    order_id = order.order_id if order else "UNKNOWN"
    customer_name = order.customer_name.split()[0] if order else "there"

    if eval_result.mode == Mode.ESCALATE_DISPATCHER:
        dest = "dispatcher"
        priority = "high"
        customer_msg = _customer_msg(channel, customer_name, order_id,
            "I'm passing this to our dispatch team — you'll hear back shortly.")

    elif eval_result.mode == Mode.ESCALATE_HUMAN:
        if eval_result.open_dispute:
            dest = "billing"
            priority = "normal"
            customer_msg = _customer_msg(channel, customer_name, order_id,
                "I'm passing this to our team — you'll hear back shortly.")
        elif "missing parcel" in eval_result.reason:
            dest = "exception_handler"
            priority = "urgent"
            customer_msg = _customer_msg(channel, customer_name, order_id,
                "I've flagged this as a priority for our team — someone will be in touch very shortly.")
        elif "exception flag" in eval_result.reason.lower():
            dest = "exception_handler"
            priority = "high"
            customer_msg = _customer_msg(channel, customer_name, order_id,
                "I'm passing this to our team — you'll hear back shortly.")
        else:
            dest = "human_agent"
            priority = "normal"
            customer_msg = _customer_msg(channel, customer_name, order_id,
                "I'm connecting you with one of our team — you'll hear back shortly.")
    else:
        raise ValueError(f"route_escalation() called with non-escalation mode: {eval_result.mode}")

    return EscalationPayload(
        destination=dest,
        priority=priority,
        order_id=order_id,
        customer_name=order.customer_name if order else None,
        reason=eval_result.reason,
        gps_age_minutes=eval_result.gps_age_minutes,
        crm_exception=eval_result.crm_exception,
        gps_exception=eval_result.gps_exception,
        open_dispute=eval_result.open_dispute,
        customer_message=customer_msg,
    )


def _customer_msg(channel: str, name: str, order_id: str, detail: str) -> str:
    if channel == "sms":
        return f"Apex order {order_id}: {detail}"
    return (f"Hi {name},\n\n"
            f"Regarding order {order_id} — {detail}\n\n"
            f"Apex Distribution Customer Operations")
