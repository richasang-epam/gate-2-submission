"""
Response Composer — Step 10 of ETA Agent pipeline.

Produces channel-appropriate customer-facing text.
Only called when mode is AUTONOMOUS or SUPERVISED — never for escalations.

Tone rules from CLAUDE.md:
  - Never give false precision.
  - Always disclose if ETA is an estimate vs confirmed window.
  - SMS: under 160 chars where possible.
  - Do not apologise for things outside scope.
"""

from dataclasses import dataclass
from app.agent.autonomy_evaluator import EvaluationResult, Mode
from app.agent.order_resolver import Order


@dataclass
class Response:
    text: str
    channel: str
    is_estimate: bool
    window_start: str
    window_end: str


def compose(order: Order,
            eval_result: EvaluationResult,
            channel: str) -> Response:

    if eval_result.mode == Mode.AUTONOMOUS:
        return _autonomous_response(order, channel)

    if eval_result.mode == Mode.SUPERVISED:
        return _supervised_response(order, eval_result, channel)

    raise ValueError(f"compose() called with non-composable mode: {eval_result.mode}")


def _autonomous_response(order: Order, channel: str) -> Response:
    start = _fmt_time(order.scheduled_window_start)
    end   = _fmt_time(order.scheduled_window_end)

    if channel == "sms":
        text = f"Your Apex delivery (order {order.order_id}) is on its way. Expected: {start}–{end}. Reply HELP to speak to our team."
    else:
        text = (
            f"Hi {order.customer_name.split()[0]},\n\n"
            f"Your delivery (order {order.order_id}) is currently en route. "
            f"Based on your driver's current position, we expect delivery between "
            f"{start} and {end} today.\n\n"
            f"If anything changes, we'll let you know. "
            f"To speak with our team, reply to this message."
        )

    return Response(text=text, channel=channel, is_estimate=True,
                    window_start=start, window_end=end)


def _supervised_response(order: Order, eval_result: EvaluationResult,
                         channel: str) -> Response:
    start = _fmt_time(order.scheduled_window_start)
    end   = _fmt_time(order.scheduled_window_end)
    # Widen window by 30 minutes either side for degraded GPS
    end_wide = _widen_end(order.scheduled_window_end)

    if channel == "sms":
        text = (f"Apex order {order.order_id}: estimated delivery {start}–{end_wide} "
                f"(estimate — our driver is currently out of signal range). "
                f"Reply HELP to speak to our team.")
    else:
        text = (
            f"Hi {order.customer_name.split()[0]},\n\n"
            f"Your delivery (order {order.order_id}) is on its way. "
            f"We currently have a limited GPS signal from your driver, so we're giving you "
            f"a slightly wider window: {start}–{end_wide} today.\n\n"
            f"This is an estimate. If you'd like a more precise update, our team is available "
            f"to help — just reply to this message."
        )

    return Response(text=text, channel=channel, is_estimate=True,
                    window_start=start, window_end=end_wide)


def _fmt_time(iso: str) -> str:
    # Expects "HH:MM" or ISO datetime — return HH:MM display
    if "T" in iso:
        return iso.split("T")[1][:5]
    return iso[:5]


def _widen_end(iso: str) -> str:
    from datetime import datetime, timedelta
    try:
        if "T" in iso:
            dt = datetime.fromisoformat(iso)
        else:
            dt = datetime.strptime(iso, "%H:%M")
        widened = dt + timedelta(minutes=30)
        return widened.strftime("%H:%M")
    except Exception:
        return iso
