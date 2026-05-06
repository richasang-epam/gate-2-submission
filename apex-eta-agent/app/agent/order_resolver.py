"""
Order Resolver — Step 2/3 of ETA Agent pipeline.

Looks up an order in Salesforce CRM using order ID as the primary key,
then falls back to customer name + postcode if not found.

In MOCK_MODE=true (default for demo) reads from mock_data/orders.json.
In production, replace _fetch_from_crm() with live Salesforce REST calls.
"""

import json
import os
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

MOCK_MODE = os.getenv("MOCK_MODE", "true").lower() == "true"
_MOCK_FILE = Path(__file__).parent.parent.parent / "mock_data" / "orders.json"


@dataclass
class Order:
    order_id: str
    customer_id: str
    customer_name: str
    postcode: str
    route_code: str
    driver_id: str
    status: str
    exception_status: bool
    scheduled_window_start: str   # ISO 8601
    scheduled_window_end: str
    acct_mgr: Optional[str] = None   # ACCT_MGR from Salesforce; non-None = strategic account


@dataclass
class OrderLookupResult:
    found: bool
    order: Optional[Order]
    lookup_method: str            # "primary" | "secondary" | "not_found"
    raw_error: Optional[str] = None


def resolve_order(order_id: str = None,
                  customer_name: str = None,
                  postcode: str = None) -> OrderLookupResult:
    if MOCK_MODE:
        return _mock_lookup(order_id, customer_name, postcode)
    return _crm_lookup(order_id, customer_name, postcode)


def _mock_lookup(order_id, customer_name, postcode) -> OrderLookupResult:
    try:
        data = json.loads(_MOCK_FILE.read_text())
    except Exception as e:
        return OrderLookupResult(found=False, order=None,
                                 lookup_method="not_found", raw_error=str(e))

    orders = {o["order_id"]: o for o in data}

    if order_id and order_id in orders:
        return OrderLookupResult(found=True,
                                 order=_dict_to_order(orders[order_id]),
                                 lookup_method="primary")

    # Secondary lookup: name + postcode
    if customer_name and postcode:
        for o in data:
            if (o["customer_name"].lower() == customer_name.lower()
                    and o["postcode"] == postcode.upper()):
                return OrderLookupResult(found=True,
                                         order=_dict_to_order(o),
                                         lookup_method="secondary")

    return OrderLookupResult(found=False, order=None, lookup_method="not_found")


def _dict_to_order(d: dict) -> Order:
    return Order(
        order_id=d["order_id"],
        customer_id=d["customer_id"],
        customer_name=d["customer_name"],
        postcode=d["postcode"],
        route_code=d["route_code"],
        driver_id=d["driver_id"],
        status=d["status"],
        exception_status=d.get("exception_status", False),
        scheduled_window_start=d["scheduled_window_start"],
        scheduled_window_end=d["scheduled_window_end"],
        acct_mgr=d.get("acct_mgr"),
    )


def _crm_lookup(order_id, customer_name, postcode) -> OrderLookupResult:
    # TODO: replace with live Salesforce REST API call
    # GET {SF_INSTANCE_URL}/services/data/v59.0/query
    #   ?q=SELECT+Id,Order_ID__c,...+FROM+Order__c+WHERE+Order_ID__c='{order_id}'
    # Confirm field names with Apex IT — see CLAUDE.md open questions
    raise NotImplementedError("Live CRM lookup not yet implemented — set MOCK_MODE=true")
