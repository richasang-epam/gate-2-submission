from flask import Blueprint, render_template

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
def index():
    demo_scenarios = [
        {
            "label": "Standard ETA — Fresh GPS",
            "description": "Typical case: fresh GPS, no flags → Autonomous response",
            "order_id": "AX-771-3344",
            "channel": "email",
            "expected_mode": "autonomous",
        },
        {
            "label": "Degraded GPS — Supervised",
            "description": "GPS 38 min old → Supervised: widened window + disclosure",
            "order_id": "AX-330-7761",
            "channel": "sms",
            "expected_mode": "supervised",
        },
        {
            "label": "Stale GPS — Escalate Dispatcher",
            "description": "GPS 72 min old → Escalate to dispatcher, no ETA given",
            "order_id": "AX-443-8812",
            "channel": "email",
            "expected_mode": "escalate_dispatcher",
        },
        {
            "label": "CRM Exception Flag",
            "description": "Exception status set on delivery record → Escalate to exception handler",
            "order_id": "AX-882-1105",
            "channel": "email",
            "expected_mode": "escalate_human",
        },
        {
            "label": "Open Billing Dispute",
            "description": "Hayes & Sons — open FUEL_SURCH_DAMAGE dispute → Escalate to billing",
            "order_id": "AX-554-9921",
            "channel": "email",
            "expected_mode": "escalate_human",
        },
        {
            "label": "Delivered — No Scan Event",
            "description": "Status shows delivered but no scan confirmation → Escalate as potential missing parcel",
            "order_id": "AX-667-2290",
            "channel": "sms",
            "expected_mode": "escalate_human",
        },
        {
            "label": "GPS Exception Flag",
            "description": "Driver App exception flag set → Escalate regardless of GPS freshness",
            "order_id": "AX-990-5544",
            "channel": "email",
            "expected_mode": "escalate_human",
        },
        {
            "label": "Order Not Found",
            "description": "Unknown order ID → Secondary lookup fails → Escalate to human agent",
            "order_id": "AX-000-0000",
            "channel": "sms",
            "expected_mode": "escalate_human",
        },
    ]

    workstream_data = {
        "labels": ["ETA Inquiries", "Delivery Exceptions", "Dispatch Adjustments", "Billing Disputes"],
        "volumes": [400, 180, 90, 60],
        "automatable_pct": [70, 25, 15, 35],
        "daily_minutes": [1600, 2160, 1620, 1680],
        "recoverable_minutes": [1120, 540, 243, 588],
        "colors": ["#2E8648", "#D47E00", "#C0392B", "#007A87"],
    }

    return render_template("dashboard.html",
                           demo_scenarios=demo_scenarios,
                           workstream_data=workstream_data)
