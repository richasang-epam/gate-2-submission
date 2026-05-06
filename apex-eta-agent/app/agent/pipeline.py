"""
ETA Agent pipeline — orchestrates all steps for a single inquiry.
"""

from dataclasses import dataclass, asdict
from typing import Optional

from app.agent.order_resolver   import resolve_order
from app.agent.gps_interpreter  import get_gps
from app.agent.autonomy_evaluator import evaluate, Mode
from app.agent.response_composer  import compose
from app.agent.escalation_router  import route_escalation
from app.agent.dispute_checker    import has_open_dispute
from app.agent import crm_logger


@dataclass
class PipelineResult:
    mode: str
    customer_message: str
    order_id: Optional[str]
    customer_name: Optional[str]
    reason: str
    gps_age_minutes: Optional[float]
    escalation_destination: Optional[str]
    case_id: str


def process_inquiry(
    raw_query: str,
    channel: str,
    order_id: str = None,
    customer_name: str = None,
    postcode: str = None,
) -> PipelineResult:

    # Step 2–3: Resolve order
    order_result = resolve_order(order_id, customer_name, postcode)

    # Step 5–8: Get GPS
    driver_id = order_result.order.driver_id if order_result.order else None
    gps_result = get_gps(driver_id) if driver_id else _unavailable_gps()

    # Exception check: open disputes
    oid = order_result.order.order_id if order_result.order else order_id
    open_dispute = has_open_dispute(oid) if oid else False

    # Step 9: Evaluate
    eval_result = evaluate(order_result, gps_result, open_dispute)

    # Step 10 or 11: Compose or escalate
    if eval_result.mode in (Mode.AUTONOMOUS, Mode.SUPERVISED):
        response = compose(order_result.order, eval_result, channel)
        customer_msg = response.text
        escalation_dest = None
    else:
        escalation = route_escalation(order_result.order, eval_result, channel)
        customer_msg = escalation.customer_message
        escalation_dest = escalation.destination

    # Step 12: Log (always)
    case = crm_logger.log_interaction(
        inquiry_channel=channel,
        raw_query=raw_query,
        order_id=oid,
        customer_id=order_result.order.customer_id if order_result.order else None,
        mode=eval_result.mode.value,
        response_text=customer_msg,
        gps_age_minutes=eval_result.gps_age_minutes,
        crm_exception_flag=eval_result.crm_exception,
        gps_exception_flag=eval_result.gps_exception,
        dispute_flag=eval_result.open_dispute,
        escalation_destination=escalation_dest,
    )

    return PipelineResult(
        mode=eval_result.mode.value,
        customer_message=customer_msg,
        order_id=oid,
        customer_name=order_result.order.customer_name if order_result.order else None,
        reason=eval_result.reason,
        gps_age_minutes=eval_result.gps_age_minutes,
        escalation_destination=escalation_dest,
        case_id=case.case_id,
    )


def _unavailable_gps():
    from app.agent.gps_interpreter import GPSResult
    return GPSResult(available=False, reading=None,
                     staleness_label="unavailable",
                     error="No driver assigned to order")
