"""
Unit tests for the Autonomy Evaluator — 11 required scenarios from CLAUDE.md.
Run: python -m pytest tests/ -v
"""

import pytest
from app.agent.autonomy_evaluator import evaluate, Mode
from app.agent.order_resolver import OrderLookupResult, Order
from app.agent.gps_interpreter import GPSResult, GPSReading


def _order(exception_status=False, status="in_transit", acct_mgr=None):
    return Order(
        order_id="AX-TEST-001",
        customer_id="C-99999",
        customer_name="Test Customer Ltd",
        postcode="B1 1AA",
        route_code="RT-99",
        driver_id="DRV-099",
        status=status,
        exception_status=exception_status,
        scheduled_window_start="13:00",
        scheduled_window_end="17:00",
        acct_mgr=acct_mgr,
    )


def _order_result(found=True, exception_status=False, status="in_transit", acct_mgr=None):
    if not found:
        return OrderLookupResult(found=False, order=None, lookup_method="not_found")
    return OrderLookupResult(found=True, order=_order(exception_status, status, acct_mgr),
                             lookup_method="primary")


def _gps(age_minutes, exception_flag=False, available=True):
    if not available:
        return GPSResult(available=False, reading=None, staleness_label="unavailable",
                         error="API unreachable")
    from app.agent.gps_interpreter import _label
    return GPSResult(
        available=True,
        reading=GPSReading(driver_id="DRV-099", lat=52.4, lon=-1.9,
                           ping_age_minutes=age_minutes, exception_flag=exception_flag),
        staleness_label=_label(age_minutes),
    )


# ── Test cases from CLAUDE.md ─────────────────────────────────────────────── #

def test_gps_fresh_no_flags():
    result = evaluate(_order_result(), _gps(10), open_dispute=False)
    assert result.mode == Mode.AUTONOMOUS


def test_gps_borderline_supervised():
    result = evaluate(_order_result(), _gps(35), open_dispute=False)
    assert result.mode == Mode.SUPERVISED


def test_gps_stale_escalate():
    result = evaluate(_order_result(), _gps(65), open_dispute=False)
    assert result.mode == Mode.ESCALATE_DISPATCHER


def test_driver_app_offline():
    result = evaluate(_order_result(), _gps(0, available=False), open_dispute=False)
    assert result.mode == Mode.ESCALATE_DISPATCHER
    assert "unavailable" in result.reason.lower() or "unreachable" in result.reason.lower()


def test_crm_exception_flag_fresh_gps():
    result = evaluate(_order_result(exception_status=True), _gps(10), open_dispute=False)
    assert result.mode == Mode.ESCALATE_HUMAN
    assert "crm exception" in result.reason.lower()


def test_open_dispute():
    result = evaluate(_order_result(), _gps(10), open_dispute=True)
    assert result.mode == Mode.ESCALATE_HUMAN
    assert "dispute" in result.reason.lower()


def test_order_not_found_primary():
    result = evaluate(_order_result(found=False), _gps(10), open_dispute=False)
    assert result.mode == Mode.ESCALATE_HUMAN
    assert "not found" in result.reason.lower()


def test_delivery_complete_no_scan():
    result = evaluate(_order_result(status="delivered_no_scan"), _gps(5), open_dispute=False)
    assert result.mode == Mode.ESCALATE_HUMAN
    assert "scan" in result.reason.lower()


def test_gps_exception_flag():
    result = evaluate(_order_result(), _gps(12, exception_flag=True), open_dispute=False)
    assert result.mode == Mode.ESCALATE_HUMAN
    assert "driver app exception" in result.reason.lower()


def test_repeat_fresh_gps_autonomous():
    """Fresh GPS, no flags, no dispute → always autonomous regardless of order count."""
    for _ in range(3):
        result = evaluate(_order_result(), _gps(8), open_dispute=False)
        assert result.mode == Mode.AUTONOMOUS


def test_supervised_gps_boundary_low():
    """GPS exactly at 30 min → still autonomous (threshold is < 30 min)."""
    result = evaluate(_order_result(), _gps(29), open_dispute=False)
    assert result.mode == Mode.AUTONOMOUS


def test_supervised_gps_boundary_high():
    """GPS at 60 min → escalate (threshold > 60 for escalation, supervised = 30–60)."""
    result = evaluate(_order_result(), _gps(60), open_dispute=False)
    assert result.mode == Mode.ESCALATE_DISPATCHER


def test_crm_exception_overrides_gps_freshness():
    """CRM exception flag should escalate even when GPS is perfectly fresh."""
    result = evaluate(_order_result(exception_status=True), _gps(2), open_dispute=False)
    assert result.mode == Mode.ESCALATE_HUMAN


def test_dispute_overrides_fresh_gps():
    """Open dispute must escalate even with fresh GPS and no other flags."""
    result = evaluate(_order_result(), _gps(5), open_dispute=True)
    assert result.mode == Mode.ESCALATE_HUMAN


def test_strategic_account_escalates():
    """Strategic account (ACCT_MGR set) must escalate to human even with fresh GPS."""
    result = evaluate(_order_result(acct_mgr="U-0089"), _gps(5), open_dispute=False)
    assert result.mode == Mode.ESCALATE_HUMAN
    assert "strategic account" in result.reason.lower() or "acct_mgr" in result.reason.lower()


def test_non_strategic_account_autonomous():
    """Orders without ACCT_MGR field should proceed to autonomous when all clear."""
    result = evaluate(_order_result(acct_mgr=None), _gps(5), open_dispute=False)
    assert result.mode == Mode.AUTONOMOUS
