# Apex Distribution Ltd — Shared Context

> **Single source of truth** for Apex facts used across all Gate 2 deliverables.  
> If a fact about Apex changes, update it here only.  
> All deliverable files reference this document rather than restating these facts.

---

## Company Profile

| Attribute | Value |
|---|---|
| Company | Apex Distribution Ltd |
| Location | Birmingham, UK (HQ) |
| Coverage | Midlands, South, and East England |
| Headcount | 800 employees |
| Fleet | 180 vehicles |
| Daily delivery volume | ~3,500 deliveries/day |
| Customer mix | B2B and DTC parcels |
| COO | Sarah Whitmore (promoted 18 months ago; 5 years prior as dispatch team lead) |

**Prior failed automation projects (critical context for any proposal):**
- **2024 customer chatbot** — customers hated it (root cause unknown: channel aversion? answer quality? bot-feel?)
- **RPA billing reconciliation** — broke when Aurum schema changed; schema changes ~quarterly without notice

---

## Customer Operations Function

**Size:** 35 people  
**Four work streams:**

| # | Work Stream | Volume/Day | Avg Handling Time | Daily Person-Minutes | % of Total Workload |
|---|---|---|---|---|---|
| 1 | ETA Inquiries | 400 | 4 min | 1,600 | 22.7% |
| 2 | Delivery Exceptions | 180 | 12 min | 2,160 | 30.6% |
| 3 | Dispatch Adjustments | 90 | 18 min | 1,620 | 22.9% |
| 4 | Billing Disputes | 60 | 28 min | 1,680 | 23.8% |
| | **Total** | **730** | | **7,060 min (~117.7 person-hours)** | **100%** |

**Capacity context:** 35 people × 7.5 hrs × 60 min = 15,750 person-minutes/day available. The four work streams consume ~7,060 min (~45%). Remaining capacity covers admin, inter-stream coordination, phone hold time, and unlogged work.

---

## System Catalogue

| System | Role | Integration Surface | Key Constraints |
|---|---|---|---|
| **Salesforce CRM** | Customer records, case history, communications | REST API confirmed | Schema detail and rate limits unknown |
| **Driver App** (in-house iOS/Android) | GPS telemetry, route assignment, scan-on-delivery, driver-to-dispatch messaging | Unknown — in-house; no API documentation referenced in brief | GPS refresh cadence unknown; Artefact 3 shows 26-min stale data in production |
| **Dispatch Console** (Java desktop, Citrix) | Route planning, driver assignment, exception triage | "Limited API surface" — Citrix-deployed | Citrix = no clean programmatic integration; RPA-class only |
| **Aurum Billing** (on-prem Oracle, since 2008) | Invoicing, fuel surcharge calculation, customer credit handling | **Batch CSV exports only** — daily 02:00–04:00 GMT | See Aurum constraints below |

### Aurum Billing — Detailed Constraints

| Constraint | Detail |
|---|---|
| No real-time API | Batch exports only; no webhook, no event stream |
| Export cadence | Daily T-1 (invoices, surcharges, credits, disputes); T-2 reconciliation (24h additional lag) |
| Invoice modification | Manual ticket to Aurum support team; typical turnaround **48 hours** |
| Fuel surcharge | Calculated automatically by route distance; **cannot be adjusted on individual invoices** by design |
| Schema stability | Changes ~quarterly **without prior notice** — this broke the prior RPA project |
| Credit audit trail | APPROVER_ID and AUDIT_REF fields exist in APEX_CREDITS.csv — formal pathway exists |
| **Credit bypass risk** | Artefact 2 + internal note: Sandra applied £170 goodwill credit via manual override with no entry in APEX_CREDITS — formal pathway being circumvented |
| APEX_CUSTOMER_MASTER cadence | Monthly refresh (1st of month) — can be up to 30 days stale |

### Aurum Batch Export Files

| File | Cadence | Contents |
|---|---|---|
| `APEX_BILL_DAILY_YYYYMMDD.csv` | T-1 daily | Invoice headers |
| `APEX_FUEL_SURCH_YYYYMMDD.csv` | T-1 daily | Fuel surcharge line items linked via INVOICE_NO |
| `APEX_CREDITS_YYYYMMDD.csv` | T-1 daily | Manual credits with APPROVER_ID, AUDIT_REF |
| `APEX_RECON_YYYYMMDD.csv` | T-2 daily | Reconciliation against received payments |
| `APEX_DISPUTES_OPEN_YYYYMMDD.csv` | T-1 daily | Open disputes snapshot (point-in-time, not transactional) |
| `APEX_AGED_RECEIVABLES_YYYYMMDD.csv` | Weekly Friday | Customer ageing buckets |
| `APEX_CUSTOMER_MASTER_YYYYMMDD.csv` | Monthly 1st | Customer reference data |

---

## Key Artefact Findings (Lived Work, Not SOP)

### Artefact 1 — Driver voicemail (Delivery Exception)
- Driver Mark Petrov, route 042, refused delivery at Stein-Allen (pallet damage question)
- **Lived reality:** Driver is parked, waiting for a human callback. No self-service resolution path. Decision requires: assess damage severity remotely, weigh account relationship (big account), consider driver's remaining 6 drops (time pressure), consult with warehouse contact.
- **SOP gap:** SOP v2.3 Section 4.3 (Damaged consignments) = INCOMPLETE — "TBD pending review of insurance protocol." Section 4.2 references DispatchHub, **retired October 2024**. SOP not updated.
- **Implication:** Dispatcher is operating on tribal knowledge, not documented protocol, for damage claims.

### Artefact 2 — Email thread (Billing Dispute, INV-2026-04318)
- Hayes & Sons (C-04451), £340 fuel surcharge on damaged delivery
- **Lived reality:** Customer waited 9+ days. Billing team bounced to Customer Ops. Customer Ops agent (Sandra) applied £170 goodwill credit — but **Aurum cannot adjust individual fuel surcharge line items**, so goodwill credit is the only lever available.
- **Critical finding:** Sandra's £170 credit has **no entry in APEX_CREDITS audit log** (internal note confirms manual override). Formal credit pathway exists (APPROVER_ID + AUDIT_REF required) but is being bypassed.
- **Cross-reference:** APEX_DISPUTES_OPEN shows D-2026-00342 (INV-2026-04318, FUEL_SURCH_DAMAGE, £340, PENDING_CLAIM) still open — Sandra's credit did not close the dispute record.
- **Pattern:** Hayes & Sons (C-04451) has 3 open or recent FUEL_SURCH_DAMAGE disputes (D-00342, D-00328, D-00318) with same customer. Repeat issue, not isolated event.

### Artefact 3 — SMS exchange (ETA Inquiry)
- Customer asking about order #AX-771-3344, route 028
- **Lived reality:** Agent looked up CRM (gave 4-hour window), then had to check with dispatch for tighter estimate. GPS last ping was 10:48 — **26 minutes before the 11:16 response and 36 minutes before the 11:24 follow-up.** Agent gave "around 14:00–15:00" as best estimate.
- **Implication:** Agent could not give a precise ETA because GPS data was stale. The 5-minute delay (11:19–11:24) was likely a manual dispatch call, not a system lookup.
- **Workflow gap:** ETA lookup currently requires a two-step process (CRM + manual dispatch call) for anything beyond the standard window.

### Artefact 4 — SOP fragment (Exception Handling SOP v2.3, Oct 2023)
- Section 4.2 (Refused deliveries): references DispatchHub (tablet) — **DispatchHub retired Oct 2024**. SOP not updated.
- Section 4.3 (Damaged consignments): **INCOMPLETE** — "TBD pending review of insurance protocol." No content.
- Section 4.4 (Unattended addresses): references Section 7, not shown.
- **Implication:** At least two live exception types (damage, unattended) have no current documented protocol. Team operates on informal knowledge.

### Artefact 5 — Aurum Batch Export data (sample, 2026-04-14)
- **APEX_FUEL_SURCH:** Fuel surcharge percentages vary by route tier (T1: 8.09%, T2: 8.15–10.04%, T3: 9.37–12.00%). Hayes & Sons on R-008 (T3, highest tier).
- **APEX_CREDITS:** Only 4 credits on 2026-04-13/14. Hayes & Sons credit (C-04451) on INV-2026-04243 (£88 GOODWILL, approved by U-0089 with AUDIT_REF) — this is a different invoice from the Artefact 2 dispute. Sandra's £170 goodwill from Artefact 2 absent.
- **APEX_RECON:** Shows DISPUTE_OPEN flags aligned with disputes file. INV-2026-04102 (C-09120 Northstar Foods) shows -£124.50 variance, ageing 30 days.
- **APEX_CUSTOMER_MASTER:** Hayes & Sons credit limit £25,000 (B2B_STANDARD); account manager U-0089 (same user who approved the £88 credit and is assigned to major accounts).
