# Deliverable 4 — Agent Purpose Document

> **Selected opportunity:** ETA Inquiries — see [D3-volume-value-analysis.md](D3-volume-value-analysis.md) for justification  
> **Delegation archetype:** Agent-led with oversight — see [D2-delegation-suitability-matrix.md](D2-delegation-suitability-matrix.md)  
> **Apex system context:** See [_shared-context.md](_shared-context.md)

---

## Agent Identity

| Field | Value |
|---|---|
| **Agent name** | Apex ETA Agent |
| **Version** | 0.1 (draft for Gate 2; not production) |
| **Owner** | Customer Operations (COO: Sarah Whitmore) |
| **Prepared by** | Richa Sang — Gate 2 assessment, 2026-05-06 |
| **Primary purpose** | Resolve delivery ETA inquiries without human intervention for the standard case |

---

## Purpose Statement

The Apex ETA Agent handles inbound "where is my delivery?" inquiries across customer contact channels. It retrieves the delivery's current route assignment and GPS-derived position from Salesforce CRM and the Driver App, interprets timing with confidence calibration, and either responds directly to the customer or escalates to a human dispatcher when data is insufficient or an exception state is detected.

It does not make operational decisions. It does not touch billing. It does not handle exceptions. It answers one question accurately and quickly: *when will my delivery arrive?*

---

## Scope

### In Scope
- Inbound ETA inquiries via SMS, email, and (if confirmed) web portal
- Order identification by reference number, customer name, or delivery address
- Route and GPS data retrieval from Salesforce CRM and Driver App
- Confidence-calibrated ETA response (window, estimate, or "uncertain — escalating")
- CRM case logging for every interaction
- Escalation routing with pre-populated context

### Out of Scope
| Excluded | Reason |
|---|---|
| Delivery exceptions (refusals, damage, missed window) | Requires dispatcher judgment; separate D1 zone map |
| Dispatch route adjustments | Citrix integration barrier; separate project |
| Billing disputes or invoice queries | Aurum constraint; separate project |
| Driver-initiated communications | Different workflow; inbound only |
| Account management or complaints handling | Relationship work; human-only |
| Credit, refund, or goodwill decisions | Never in scope for this agent |

---

## KPIs

| KPI | Target | Measurement Method | Baseline (if known) |
|---|---|---|---|
| First-contact resolution rate | ≥ 85% resolved without human handoff | CRM: escalation flag on cases | Unknown — discovery question |
| Avg agent response time | < 2 minutes (vs ~4 min current) | CRM: inquiry timestamp to response timestamp | ~4 min (scenario brief) |
| Escalation rate | < 20% of ETA inquiries escalated | CRM: escalation cases / total ETA cases | Unknown |
| GPS-stale escalations (as % of total) | < 10% | Agent audit log: staleness trigger events | Unknown — depends on GPS cadence |
| Customer satisfaction (CSAT) | ≥ current CSAT baseline | Post-interaction survey (if deployed) | Unknown — discovery question |
| False precision errors | 0 | Audit log: responses given with GPS data > 60 min stale | n/a |

*Note: CSAT baseline and current escalation rate are both discovery questions (see D6). Targets will be revised once baselines are confirmed.*

---

## ETA Confidence Tier Definition

Confidence tier is a structured uncertainty signal — not a precise probability. It controls customer-facing language and determines whether a human review flag is raised.

| Tier | Conditions | Customer-Facing Language |
|---|---|---|
| **Tier 1 — Moderate confidence** | GPS ≤30 min; no exception flag | "Your delivery is currently estimated to arrive between [window]. Our last tracking update was [X] minutes ago." |
| **Tier 2 — Low confidence** | GPS 30–60 min; no exception flag | "Your delivery is estimated to arrive [window], though our tracking is [X] minutes old. We'll update you if anything changes significantly." |
| **Tier 3 — Insufficient data** | GPS >60 min; exception flag active; Driver App unreachable | Escalate. No ETA sent to customer. Agent handles. |

Even Tier 1 responses carry uncertainty: fresh GPS confirms a driver's last known location but does not capture route reprioritisation, failed prior drops, parking delays, or driver discretion on stop sequence. Tier 1 language uses window estimates, not point-in-time precision.

---

## Autonomy Matrix

The agent operates in four modes. Mode is determined by evaluating conditions in order (top to bottom).

| Mode | Conditions | Agent Action | Human Role |
|---|---|---|---|
| **Autonomous** | Order found; GPS ping < 30 min old (Tier 1); no exception flag | Respond with best-estimate ETA window. Log CRM case. | None — passive monitoring via dashboard |
| **Supervised** | Order found; GPS ping 30–60 min stale (Tier 2); no exception flag | Respond with widened window + explicit staleness disclosure. Flag case for supervisor review. | Supervisor can override or add note; not required to act |
| **Escalate to Dispatcher** | GPS ping > 60 min stale (Tier 3); OR Driver App unreachable; OR order in exception state (any source); OR order not found after secondary lookup | Escalate with pre-populated context: order, route, driver, GPS last known, exception flag. Tell customer they'll receive an update shortly. | Dispatcher responds within SLA (confirm SLA — discovery question) |
| **Escalate to Human Agent** | Customer has submitted > 1 inquiry on same order within 24h; OR customer uses explicit escalation/complaint language; OR order in active billing dispute; OR customer identified as strategic account (ACCT_MGR field in Salesforce) | Route to named human agent. Do not give ETA. | Human agent handles full interaction |

**Principle: when mode is ambiguous, escalate. Never infer. Never guess.**

---

## Escalation Triggers (complete list)

1. GPS last ping timestamp > 60 minutes old
2. Driver App API unavailable or returning errors
3. Order status flagged as exception in CRM or Driver App (any exception type)
4. Order not found in CRM after: primary lookup (order ID) AND secondary lookup (name + address)
5. Same customer has submitted > 1 ETA inquiry for the same order within a 24-hour window
6. Customer message contains explicit escalation or complaint language (detection list: TBD with ops team)
7. Order has an open dispute record in billing system (cross-reference against APEX_DISPUTES_OPEN batch, updated daily)
8. Delivery marked as completed (scan-on-delivery confirmed) but customer is still inquiring → potential missing parcel; escalate immediately
9. Customer identified as strategic account — `[VALIDATED — Gate 2 Artifacts]` ACCT_MGR field confirmed in APEX_CUSTOMER_MASTER. Route where CUSTOMER_ID maps to a named ACCT_MGR (e.g., U-0089 for Hayes & Sons, Severn Wholesale, Travis & Mason) to that agent's named queue. Uniform agent responses for named-account customers carry reputational and contractual risk that does not appear in individual-case blast-radius calculations. **Build-ready.**

---

## Activity Catalogue

| Step | Activity | System | Mode |
|---|---|---|---|
| 1 | Parse inbound message → extract order reference | Comms gateway (SMS/email) | Autonomous |
| 2 | Primary CRM lookup: order ID → customer record → delivery record | Salesforce CRM (REST) | Autonomous |
| 3 | Secondary CRM lookup if no match: customer name + delivery address | Salesforce CRM (REST) | Autonomous |
| 4 | Pull route assignment from delivery record | Salesforce CRM (REST) | Autonomous |
| 5 | Query Driver App: route → driver → GPS last ping → delivery sequence | Driver App (REST assumed) | Autonomous |
| 6 | Evaluate GPS staleness: compare ping timestamp to current time | Internal logic | Autonomous |
| 7 | Check exception flags: CRM exception status + Driver App status | CRM + Driver App | Autonomous |
| 8 | Check dispute cross-reference: APEX_DISPUTES_OPEN (T-1 batch) | Daily ingested CSV | Autonomous |
| 9 | Apply autonomy matrix → determine mode | Internal rules engine | Autonomous |
| 10 | Compose response (Autonomous/Supervised) or prepare escalation context | Comms gateway / CRM | Autonomous or Supervised |
| 11 | Send response or route escalation with context | Comms gateway / CRM | Autonomous or Human-triggered |
| 12 | Log CRM case: channel, query text, mode triggered, response given, escalation Y/N, GPS staleness at time | Salesforce CRM (REST) | Autonomous |

---

## Failure Modes and Mitigations

| Failure Mode | Likelihood | Impact | Mitigation |
|---|---|---|---|
| GPS data stale (driver app not syncing — rural/tunnel coverage) | Medium | High — agent gives ETA for driver who has diverted or stopped | Hard staleness thresholds (30/60 min). Never extrapolate GPS position beyond threshold. |
| Order in exception but CRM not yet updated (dispatcher lag) | Medium | High — agent tells customer delivery is coming; it won't | Cross-check both CRM and Driver App exception flags; if discrepancy, escalate |
| Multiple orders for same customer (B2B accounts often have several) | Medium | Low — addressable | Secondary lookup by invoice/address if first order match is ambiguous; present options to customer |
| Driver App backend unavailable (maintenance, outage) | Low | High — agent cannot retrieve GPS; cannot answer safely | Immediate escalation on any Driver App API error; do not cache stale GPS as "good enough" |
| Customer gives order number from a different carrier | Low | Low | No match after secondary lookup → escalate; do not fabricate |
| Agent confirms delivery but parcel is missing | Low | Very High — generates complaint and potential claim | Only confirm delivery when scan-on-delivery event is explicitly present. Missing-parcel escalate immediately. |
| Dispute batch CSV not updated (Aurum export failure) | Low | Medium — agent may respond to a customer whose order is under dispute | Log warning when batch is missing; fall back to treating dispute flag as unknown; escalate for any billing-adjacent query |

---

## System Dependencies

| System | What Agent Needs | Integration Mode | Risk |
|---|---|---|---|
| Salesforce CRM | Order records, delivery record, customer profile, case write | REST API | Low — confirmed |
| Driver App backend | GPS last ping (timestamp + coordinates), route, delivery sequence, exception flags | REST API (assumed — not confirmed) | **Medium — must confirm before build** |
| Comms gateway | SMS receive/send, email webhook receive/send | Webhook + REST | Low — channel already operational |
| Aurum APEX_DISPUTES_OPEN (daily batch) | Cross-reference dispute flag on order before responding | Daily CSV ingestion to query layer | Low — batch exists; pipeline needed |

*Full system detail: see [D5-system-data-inventory.md](D5-system-data-inventory.md)*

---

## Open Questions / Assumptions

These items must be resolved before committing to production build. They are surfaced in [D6-discovery-questions.md](D6-discovery-questions.md).

| Item | Current assumption | Confidence | Blocking? |
|---|---|---|---|
| Driver App has external REST API | Assumed — in-house app has a backend service queryable by other systems | Medium | **Yes — do not build GPS integration without confirming** |
| GPS refresh cadence | Assumed 5–10 min; Artefact 3 shows 26-min stale gap in production | Low | Yes — affects threshold logic |
| CRM-to-Driver-App linkage field | Assumed route_code in CRM links to Driver App | Medium | Yes — need Salesforce schema |
| ETA inquiry channel split (SMS / email / phone / web) | Unknown — 400/day total; proportions unknown | Low | Partially — affects build scope |
| Salesforce API rate limits | Unknown | Low | Partially — affects batch query design |
| Customer CSAT baseline | Unknown | n/a | No — needed for KPI calibration post-launch |
| SLA for dispatcher response on escalated cases | Unknown | Low | No — needed for customer message ("we'll update you shortly") |

---

## Pilot Governance Model

AERA is a constrained pilot, not a production replacement for Customer Operations judgment. Human oversight remains active throughout.

**Ownership:**
- **Executive sponsor:** Sarah Whitmore — final authority on scope, expansion gates, and rollback decisions
- **Operational ownership:** Customer Operations leadership + dispatch supervisors — escalation quality and handling-pattern monitoring
- **Technical ownership:** Salesforce integration team + Driver App support — API reliability and data quality

**Weekly calibration signals:**
- ETA re-contact rate (same customer, same order, same day) — target <15%
- Escalation rate by confidence tier (Tier 1/2/3 tracked separately; shift indicates threshold miscalibration)
- False-precision complaints (ETA accuracy disputes in Salesforce; >5% triggers threshold review)
- Dispatcher bypass behaviour (ETA cases handled manually despite AERA eligibility — trust gap signal, not discipline problem)
- Strategic account handling outcomes (reviewed separately; any account manager dissatisfaction triggers immediate review)

**Rollback conditions — suspend pilot immediately if:**
- Re-contact rate >25% sustained over 3 days
- Escalation accuracy <80% sustained over 7 days
- Bypass rate >40% of eligible ETA cases over 14 days
- Three or more route-level complaint clusters in a single day (indicates exception flag lag masking route failures)
- Dispatchers or account managers explicitly request suspension

Rollback = full reversion to human-handled ETA queue. No partial degradation mode.

**Expansion gate — no expansion into exception arbitration, dispatch coordination, or billing orchestration until:**
1. ≥60 days sustained performance within KPI targets
2. Escalation accuracy ≥90% with <10% human override rate
3. Bypass rate <10% with no shadow workflows detected
4. Zero strategic account escalations to Sarah Whitmore

Expansion requires explicit Sarah Whitmore sign-off and updated APD scope. It is not automatic.

---

## KPI Gaming Risks

| Risk | Mechanism | Mitigation |
|---|---|---|
| Rubber-stamped escalations | Agents nominally review but functionally accept AERA outputs — oversight becomes illusory | 10% weekly qualitative case sampling on decision quality, not only escalation accuracy |
| Handling-time deflation | Agents speed-process under measurement pressure to inflate time-freed KPI | Track decision quality and re-contact rate on escalated cases separately from throughput |
| ETA window widening | Dispatchers extend windows to reduce false-precision complaint rate | Track nominal delivery window width as a secondary trend signal across the pilot |
| Escalation gaming | Agents inflate or suppress escalations to affect KPI narrative | Escalation rate is a calibration input, not a success metric — interpret only with re-contact rate and decision quality |

Quantitative KPIs require a parallel qualitative review programme — weekly 10% case sampling, bi-weekly dispatcher sentiment check-ins, monthly handling-pattern audit.

---

## Organisational Rejection Risks

| Risk | Mechanism | Mitigation |
|---|---|---|
| Dispatcher ownership resistance | Named-dispatcher routing creates implicit route ownership; shared agent queue perceived as depersonalising accountability | Co-design queue architecture with dispatchers before build; exception pre-assembly must route to named dispatcher, not generic pool |
| Bypass behaviour | Agents who distrust AERA's confidence tiers handle ETA cases manually, negating compression value | Monitor handling rate split weekly; treat systematic bypass as threshold miscalibration signal, not a discipline problem |
| Trust erosion from false precision | A sequence of wrong ETAs causes the team to lose confidence in all AERA outputs; trust erodes asymmetrically | Surface weekly error analysis visibly to the team; do not obscure incorrect estimates |
| Judgment displacement anxiety | Agents or dispatchers fear AERA expansion into exception classification | Communicate APD scope split explicitly at launch: MVP scope / Pilot scope / Future scope (blocked with named prerequisites) |
| Surveillance perception | GPS logging perceived by drivers as individual performance monitoring | Frame AERA as team capacity tool; GPS data scoped to ETA estimation only — not accessible for driver performance evaluation |

**Adoption failure is a first-class risk.** A technically correct AERA deployment that dispatchers bypass is operationally equivalent to a failed deployment — and may be harder to recover from as the third failed automation initiative.

---

## Secondary Build Scope: Exception Context Pre-Assembly

*(Build-ready; Phase 1b — deploy alongside or immediately after AERA pilot. Shares Salesforce + Driver App API surface.)*

On exception case creation in Salesforce, automatically populate: customer record and account flags, order history, prior exception cases, consignment value with >£500 Duty Manager escalation flag, and current GPS status for the assigned driver.

**In scope:** Pre-assembled context panel in Salesforce case view before dispatcher action.  
**Out of scope:** Exception classification, disposition recommendation, driver/depot communication, any routing decision.  
**Critical dependency:** Named-dispatcher routing model must be confirmed (D6 Q7). If dispatchers hold named-route ownership, exception context must surface in the named dispatcher's queue — not a generic pool.

---

## Build Instruction

> This document is intended to be specific enough that an AI coding agent can begin building. See [CLAUDE.md](CLAUDE.md) for project constraints, delegation boundaries, and what not to build in Phase 1.

Start with: Activity steps 1–4 (parse → CRM lookup → route retrieval). These are deterministic, depend only on confirmed-available Salesforce CRM API, and can be unit-tested with mock data before Driver App integration is confirmed. Do not begin GPS integration (steps 5–8) until Driver App API spec is confirmed.
