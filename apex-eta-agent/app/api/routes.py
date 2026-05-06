from flask import Blueprint, request, jsonify
from app.agent.pipeline import process_inquiry
from app.agent import crm_logger

api_bp = Blueprint("api", __name__)


@api_bp.route("/inquiry", methods=["POST"])
def inquiry():
    body = request.get_json(force=True, silent=True) or {}
    order_id      = body.get("order_id", "").strip() or None
    customer_name = body.get("customer_name", "").strip() or None
    postcode      = body.get("postcode", "").strip() or None
    channel       = body.get("channel", "email").strip().lower()
    raw_query     = body.get("raw_query", f"Where is order {order_id}?")

    if not order_id and not (customer_name and postcode):
        return jsonify({"error": "Provide order_id or customer_name + postcode"}), 400

    result = process_inquiry(
        raw_query=raw_query,
        channel=channel,
        order_id=order_id,
        customer_name=customer_name,
        postcode=postcode,
    )

    return jsonify({
        "case_id":               result.case_id,
        "mode":                  result.mode,
        "customer_message":      result.customer_message,
        "order_id":              result.order_id,
        "customer_name":         result.customer_name,
        "reason":                result.reason,
        "gps_age_minutes":       result.gps_age_minutes,
        "escalation_destination": result.escalation_destination,
    })


@api_bp.route("/interactions", methods=["GET"])
def interactions():
    limit = min(int(request.args.get("limit", 50)), 200)
    return jsonify(crm_logger.get_recent_interactions(limit))


@api_bp.route("/stats", methods=["GET"])
def stats():
    log = crm_logger.get_recent_interactions(1000)

    total = len(log)
    if total == 0:
        return jsonify({
            "total": 0, "autonomous_pct": 0, "supervised_pct": 0,
            "escalated_pct": 0, "avg_gps_age": None,
        })

    modes = [e["mode"] for e in log]
    auto_n = sum(1 for m in modes if m == "autonomous")
    sup_n  = sum(1 for m in modes if m == "supervised")
    esc_n  = total - auto_n - sup_n

    ages = [e["gps_age_minutes"] for e in log if e["gps_age_minutes"] is not None]
    avg_age = round(sum(ages) / len(ages), 1) if ages else None

    escalation_dests = {}
    for e in log:
        d = e.get("escalation_destination")
        if d:
            escalation_dests[d] = escalation_dests.get(d, 0) + 1

    return jsonify({
        "total": total,
        "autonomous_count": auto_n,
        "supervised_count": sup_n,
        "escalated_count": esc_n,
        "autonomous_pct": round(auto_n / total * 100, 1),
        "supervised_pct": round(sup_n  / total * 100, 1),
        "escalated_pct":  round(esc_n  / total * 100, 1),
        "avg_gps_age_minutes": avg_age,
        "escalation_destinations": escalation_dests,
    })
