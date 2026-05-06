# Deliverable 5 — System / Data Inventory

> **Full system catalogue and Aurum constraints:** See [_shared-context.md](_shared-context.md)  
> **Agent system dependencies:** See [D4-agent-purpose-document.md](D4-agent-purpose-document.md)

This deliverable maps what the agent needs, what is confirmed available, what is assumed, what is missing, and what is risky. It also covers all four work streams (not just the ETA agent) because the system landscape affects the delegation architecture across all of them.

---

## System Inventory

### 1. Salesforce CRM

| Attribute | Status | Detail |
|---|---|---|
| **Role** | Customer master, case history, delivery records, communications log | Confirmed in brief |
| **Integration surface** | REST API | Confirmed |
| **Availability** | High confidence | Stated in brief |
| **What ETA agent needs** | Order ID → delivery record → route assignment; customer profile; case write; exception flag | Required for all phases |
| **What exception agent needs** | Account tier, credit limit, contract type, prior exception history | Required for context assembly |
| **What billing dispute agent needs** | Case history, prior dispute records, customer comms | Required for triage |
| **Known gaps** | Field-level schema unknown; whether order records link directly to Driver App route codes not confirmed; Salesforce tier / API rate limits unknown | Discovery question |
| **Risk** | Low — modern API-first CRM | — |
| **Assumption** | Salesforce delivery record contains route_code (or equivalent) that links to Driver App | Confidence: **Medium** |

### 2. Driver App (in-house iOS/Android)

| Attribute | Status | Detail |
|---|---|---|
| **Role** | GPS telemetry, route and delivery sequence, scan-on-delivery events, driver-to-dispatch messaging | Confirmed in brief |
| **Integration surface** | **Unknown** — in-house app; no API documentation referenced | Not confirmed |
| **Availability** | App confirmed; backend API not confirmed | — |
| **What ETA agent needs** | GPS last ping (timestamp + coordinates), delivery sequence position, exception flags on delivery, scan-on-delivery event | Required before GPS phase |
| **Known gaps** | No API spec available. GPS refresh cadence unknown. Artefact 3 shows 26-min stale data was a production event. Whether Driver App pushes events or requires polling: unknown. | **Critical gap** |
| **Risk** | **Medium-High** — in-house app may have undocumented backend; GPS staleness in production suggests either infrequent polling or coverage gaps | — |
| **Assumption** | Driver App backend exposes REST API queryable by other internal systems | Confidence: **Medium** |
| **Assumption** | GPS telemetry is refreshed at least every 5–10 minutes under normal conditions | Confidence: **Low** (Artefact 3 contradicts this; 26-min gap observed) |
| **Blocking item** | Do not build GPS integration until API spec is confirmed. See [D4-agent-purpose-document.md](D4-agent-purpose-document.md). | |

### 3. Dispatch Console (Java desktop, Citrix)

| Attribute | Status | Detail |
|---|---|---|
| **Role** | Route planning, driver assignment, exception triage | Confirmed |
| **Integration surface** | "Limited API surface" — Citrix-deployed | Confirmed (limited) |
| **What dispatch adjustment agent would need** | Read/write access to routes, driver assignments, and exception queue | Not available cleanly |
| **Integration barrier** | Citrix = no standard programmatic interface; any integration is RPA-class (screen scraping, UI automation) or requires a significant re-platforming of the Dispatch Console | Hard constraint |
| **Risk** | **High** — Citrix integration is inherently brittle (same failure mode as prior RPA project); schema changes to UI would break any automation | — |
| **Recommendation** | Do not attempt Dispatch Console integration in Phase 1 or Phase 2. Any dispatch automation must wait for a Dispatch Console API re-platform (separate project, multi-year). | — |

### 4. Aurum Billing (on-prem Oracle, 2008)

*Full constraint detail in [_shared-context.md](_shared-context.md#aurum-billing--detailed-constraints)*

| Attribute | Status | Detail |
|---|---|---|
| **Role** | Invoicing, fuel surcharges, credits, reconciliation | Confirmed |
| **Integration surface** | **Batch CSV only** — no real-time API, no webhook | Confirmed hard constraint |
| **What billing dispute agent needs** | Invoice data, surcharge breakdown, credit history, dispute status | Available in T-1 batch |
| **What is NOT available** | Real-time invoice lookup; real-time credit application; individual line-item adjustment | Hard constraint by Aurum design |
| **Invoice modification path** | Manual ticket to Aurum support team; 48h typical turnaround | Hard constraint |
| **Schema stability** | Changes ~quarterly without prior notice | **Critical risk — killed prior RPA project** |
| **Credit audit gap** | Artefact 2 + internal note: Sandra applied £170 credit with no APEX_CREDITS entry — formal pathway bypassed | **Governance risk** |
| **Risk rating** | **Critical** for any agentic integration | — |

**Aurum-specific mitigations (required before any billing agent work):**

1. **Schema monitoring:** On every daily batch import, hash-compare CSV headers against last-known schema. Alert immediately on any change before processing. Never silently accept a schema mutation.
2. **Operational query layer:** Ingest daily batch at 04:30 GMT (after export window closes) into an internal query-able database. Agent queries this layer, never the raw CSV files directly.
3. **T-1 data disclosure:** All agent responses that use Aurum data must disclose "based on data as of [yesterday's date]". Never present batch data as current.
4. **Credit staging pathway:** Agent may propose a credit for human approval only. Any proposed credit must be routed through the formal APPROVER_ID + AUDIT_REF pathway. The manual override pattern must be blocked, not automated.
5. **48h modification acknowledgement:** When a dispute requires an invoice modification (not a goodwill credit), agent must communicate the 48h turnaround to the customer immediately, not after the ticket is raised.

---

## Data Availability Matrix (by agent activity)

| Data Item | Source | Available? | Latency | Risk |
|---|---|---|---|---|
| Order ID → customer record | Salesforce CRM | Yes (API) | Real-time | Low |
| Order ID → route assignment | Salesforce CRM | Yes (assumed schema) | Real-time | Medium (schema assumption) |
| Route → driver → GPS last ping | Driver App backend | Assumed | Real-time (assumed) | **High — API not confirmed** |
| GPS ping timestamp | Driver App backend | Assumed | Real-time (assumed) | **High — refresh cadence unknown** |
| Exception flag on delivery | CRM + Driver App | Partial | CRM real-time; Driver App assumed | Medium |
| Scan-on-delivery event | Driver App backend | Assumed | Real-time (assumed) | Medium |
| Invoice data (for dispute triage) | Aurum batch | Yes (CSV) | T-1 (24h lag) | Medium — schema change risk |
| Fuel surcharge breakdown | Aurum batch | Yes (CSV) | T-1 | Medium |
| Credit history | Aurum batch | Yes (CSV) — but with bypass gap | T-1 | **High — audit trail incomplete** |
| Open disputes snapshot | Aurum batch | Yes (CSV) | T-1 | Medium |
| Customer master | Aurum batch | Yes (CSV) | Monthly | Low (for reference only) |
| Aged receivables | Aurum batch | Yes (CSV) | Weekly | Low |

---

## Assumptions Register

Every inference about systems or data that the brief did not confirm is listed here with confidence level and how to test it.

| # | Assumption | Confidence | How to Test / Validate |
|---|---|---|---|
| A1 | Driver App backend exposes a REST API queryable by other systems | **Medium** | Architecture review session with the in-house app team |
| A2 | GPS telemetry refreshes every 5–10 minutes under normal conditions | **Low** (Artefact 3 shows 26-min gap in production) | Ask Driver App team for telemetry polling spec; pull 30-day GPS lag histogram |
| A3 | Salesforce CRM delivery records contain a route_code field linking to Driver App | **Medium** | Salesforce schema review with IT / CRM admin |
| A4 | The ETA inquiry channel split (400/day) includes SMS, email, and possibly a web portal | **Low** | Analytics pull from CRM case source field |
| A5 | Salesforce API rate limits are not a constraint at 400 cases/day | **Low** | Confirm Salesforce license tier with IT |
| A6 | A customer-facing web portal or parcel tracking page exists (typical for regional carrier) | **Low** | Confirm with Sarah Whitmore |
| A7 | The Driver App "exception flags" are propagated to CRM in near-real-time | **Medium** | Test: create a test exception in Driver App and observe CRM latency |
| A8 | A dispatcher has a defined SLA for responding to escalated ETA cases | **Low** | Operational process question for Sarah |
| A9 | Aurum does not have any read API beyond the batch exports | **High confidence** (brief explicit; prior RPA project confirms) | Check with Aurum support / IT as formality |
| A10 | The Dispatch Console's "limited API surface" means no write access | **High confidence** | Technical spike with IT to map what the API surface covers |

---

## What Is Risky (Summary)

| Item | Risk Type | Impact if Wrong |
|---|---|---|
| Driver App API availability | Integration risk | GPS integration phase blocked; ETA agent limited to CRM window only |
| GPS refresh cadence | Data quality risk | Agent gives false-precision estimates more frequently than planned |
| Aurum schema changes | Fragility risk | Billing triage agent breaks silently on next quarterly schema change |
| Credit audit bypass pattern | Governance risk | Billing agent built on top of a compromised audit trail; financial control gap widens |
| SOP 4.3 incompleteness | Process risk | Exception context assembly agent has no rule set for damage cases; outputs are unreliable |
| Citrix integration barrier | Technical risk | Any attempt to automate Dispatch Adjustments before re-platform fails like the prior RPA project |

---

## Shadow Systems and Undocumented Dependencies

| Shadow System | Observed In | Risk |
|---|---|---|
| Named-dispatcher personal queues | Artefact 1: Mark routes specifically to Sandra, not shared dispatch line | **High** — single point of failure; no documented handoff; any agent queue design must account for named routing expectations or dispatchers will ignore the queue |
| Tribal knowledge: Aurum goodwill credit workaround | Artefact 2: Sandra's resolution method — manual override, unstated authority | **High** — undocumented; compliance risk; credit authority ceiling unknown; not replicable by agent without audit trail |
| Credits audit log bypass | Artefact 2 internal note; `[VALIDATED]` APEX_CREDITS confirms intermittent failure | **Critical** — agent must not replicate. Any agent output touching credits must be logged in Salesforce, not only in Aurum. The Aurum credits CSV cannot be relied upon as a complete record. |
| Informal customer pattern awareness | Artefact 2: "second time this quarter" — `[VALIDATED]` Hayes & Sons (C-04451) has 3 open disputes in 7 weeks, all assigned to Sandra W. | Agent opportunity via Salesforce history — observable via repeat dispute flag. **MVP value confirmed.** |

---

## Missing Systems / Blocked Integrations

| Gap | Impact on Design | Resolution Path |
|---|---|---|
| Aurum real-time API | Billing dispute resolution blocked; structural T-1 lag | Long-term: Aurum replacement or real-time middleware. Short-term: batch context pre-assembly with explicit lag caveat and schema-diff monitoring as prerequisite. |
| Dispatch Console API undefined | Exception decision support blocked; dispatch adjustment orchestration blocked | Engineering discovery sprint required. Treat as blocked until API scope confirmed in writing. |
| Cross-case linkage (exception ↔ billing dispute) | Same-consignment disputes require manual cross-reference across two Salesforce records | Short-term: Salesforce custom field linking exception case to billing dispute case, populated manually at intake. Longer-term: automated match on shared order number at case creation. |
| SOP knowledge base (current) | SOP v2.3 cannot be used for agent decision logic — references retired tools, incomplete damage protocol | Prerequisite: SOP revised and signed off by Sarah Whitmore. Human process dependency, not technical. |
