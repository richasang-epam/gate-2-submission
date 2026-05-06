# Gate 2 — Richa Sang

**Submission date:** 2026-05-06  
**Scenario:** Apex Distribution Ltd — Customer Operations Agentic Transformation  
**Format:** All seven deliverables in one document (headings navigate each deliverable)

---

## Artefact-Driven Evidence Summary

All design decisions are grounded in source evidence. Confidence is assigned before building — not after.

| Source | Type | Confidence Weight |
|---|---|---|
| Scenario brief (volumes, tooling, stakeholder context) | Explicit fact | High |
| Artefact 1 — Driver voicemail (Mark Petrov) | Lived-work signal | High |
| Artefact 2 — Billing dispute thread (Hayes & Sons) | Lived-work signal | High |
| Artefact 3 — ETA SMS exchange | Lived-work signal | High |
| Artefact 4 — SOP v2.3 (Oct 2023) | Documented workflow — partially obsolete | Low–Medium |
| Artefact 5 — Aurum batch export catalogue | System constraint evidence | High |
| Gate 2 Artifacts — Aurum CSV exports (Apr 2026) | System data validation + repeat pattern evidence | High |
| Industry benchmarks (logistics AI, ops automation) | Assumption / orientation only | Low — must not drive design |

**Key contradictions identified:**
1. **SOP v2.3 references DispatchHub** — retired October 2024. Real tool is Driver App. Any design built against the SOP is wrong.
2. **SOP Section 4.3 (Damaged consignments)** — blank. No documented protocol exists for the operationally most complex exception type.
3. **Credits audit gap is intermittent, not systematic** — `[VALIDATED — Gate 2 Artifacts]` APEX_CREDITS_20260414.csv shows proper APPROVER_ID + AUDIT_REF structure for Hayes & Sons £88 credit (CR-2026-00814), confirming the bypass in Artefact 2 is unpredictable, not universal. Non-deterministic failure is operationally worse than systematic failure.
4. **Hayes & Sons repeat pattern confirmed** — `[VALIDATED — Gate 2 Artifacts]` APEX_DISPUTES_OPEN shows 3 open disputes in 7 weeks (D-2026-00318 Feb 28, D-2026-00337 Mar 28, D-2026-00342 Apr 15), all FUEL_SURCH_DAMAGE, all assigned to Sandra W. 57% of open disputes are FUEL_SURCH_DAMAGE type.
5. **ACCT_MGR field exists in Salesforce** — `[VALIDATED — Gate 2 Artifacts]` APEX_CUSTOMER_MASTER confirms named account management structure. Hayes & Sons (C-04451), Severn Wholesale, Travis & Mason all assigned to U-0089 (Sandra W.). Strategic account escalation routing is build-ready.

---

## Reviewer Navigation

| Deliverable | Key Finding |
|---|---|
| 1 — Cognitive Load Map | SOP is partially obsolete; dispatcher judgment and named-routing patterns are the real operating protocol; hidden work fragments every work stream |
| 2 — Delegation Suitability Matrix | No work stream qualifies for full autonomy; ETA standard is the only agent-led candidate; scored 4.2/5 |
| 3 — Volume × Value | MVP selected for blast radius and reversibility, not peak savings; three opportunities build-ready, two blocked, one multi-year |
| 4 — Agent Purpose Document | AERA is a trust-recovery mechanism before it is a productivity intervention; pilot governance and rollback conditions specified |
| 5 — System/Data Inventory | Constraints documented as first-class design inputs; shadow systems and blocked integrations mapped |
| 6 — Discovery Questions | Eleven questions that would materially change delegation boundaries or feasibility |
| 7 — CLAUDE.md | Anti-overautomation and adoption failure treated as co-equal risks to technical failure |

---

## Context: Apex Distribution Ltd

**Company:** Apex Distribution Ltd, Birmingham, UK. Regional carrier, Midlands/South/East England. 800 employees, 180 vehicles, ~3,500 deliveries/day (B2B and DTC).  
**COO:** Sarah Whitmore — 5 years on dispatch, promoted 18 months ago. Sceptical of consultants and chatbots after two failed projects: 2024 customer chatbot (customers hated it) and an RPA billing project (broke on quarterly Aurum schema changes).

**Work streams:**

| Work Stream | Volume/Day | Avg Handling Time | Daily Person-Minutes | % of Workload |
|---|---|---|---|---|
| ETA Inquiries | 400 | 4 min | 1,600 | 22.7% |
| Delivery Exceptions | 180 | 12 min | 2,160 | 30.6% |
| Dispatch Adjustments | 90 | 18 min | 1,620 | 22.9% |
| Billing Disputes | 60 | 28 min | 1,680 | 23.8% |
| **Total** | **730** | | **7,060 min (~117.7 hrs)** | 100% |

**System catalogue:**

| System | Integration Surface | Key Constraint |
|---|---|---|
| Salesforce CRM | REST API (confirmed) | Schema detail unknown |
| Driver App (in-house iOS/Android) | Unknown — no API spec | GPS refresh cadence unknown; 26-min stale data observed |
| Dispatch Console (Java/Citrix) | "Limited API surface" | Citrix = no clean integration path |
| Aurum Billing (on-prem Oracle, 2008) | **Batch CSV only** — 7 files, T-1/T-2 | No real-time API; schema changes quarterly without notice |

**Key artefact findings (lived work, not SOP):**
- **Artefact 1:** Driver parked awaiting human call-back on damage/refusal decision. SOP 4.3 blank — "TBD pending insurance protocol review." SOP still references retired DispatchHub.
- **Artefact 2:** Hayes & Sons dispute INV-2026-04318. Sandra applied £170 goodwill credit via manual override — no APEX_CREDITS audit log entry. Dispute still shows PENDING_CLAIM (D-2026-00342) — credit did not close the record.
- **Artefact 3:** Agent gave 4-hour window, then manually contacted dispatch to narrow to 14:00–15:00. GPS last ping was 26 min stale at response time.
- **Artefact 4:** Section 4.2 references DispatchHub (retired); Section 4.3 blank; team operates on tribal knowledge for damage and unattended cases.
- **Artefact 5:** Aurum CSV cross-file linkage via INVOICE_NO works; credit audit trail schema exists (APPROVER_ID, AUDIT_REF) but is bypassed; Hayes & Sons has 3 FUEL_SURCH_DAMAGE disputes in 2026 — recurring, not isolated.

**Gate 2 Artifact updates (Aurum CSV exports, Apr 2026):**
- `[VALIDATED]` Hayes & Sons: 3 open disputes in 7 weeks; 57% of all open disputes are FUEL_SURCH_DAMAGE. Repeat-pattern flag is active, not hypothetical.
- `[VALIDATED]` Audit bypass is intermittent: APEX_CREDITS shows proper structure for some credits (CR-2026-00814, £88), bypass for others. Non-deterministic failure is operationally worse than systematic.
- `[VALIDATED]` ACCT_MGR field confirmed in APEX_CUSTOMER_MASTER. Strategic account escalation routing is build-ready.
- `[VALIDATED]` APEX_FUEL_SURCH confirms route-based tiering (T1/T2/T3, 8.09%–12.00%). Individual surcharge adjustment requires manual Aurum ticket.

---

## Deliverable 1 — Cognitive Load Map

### Work Stream 1: ETA Inquiries (400/day, 4 min avg)

**What actually happens:** Agent looks up CRM, gets a 4-hour window, then manually contacts dispatch to narrow the estimate. GPS data was 26–36 minutes stale. Agent gives a human best-guess, not a system-computed result. No SOP exists for ETA inquiries; the workflow is entirely informal.

**Job sequence:** Identify order → retrieve delivery status (route, driver, GPS, window) → interpret timing with confidence calibration → communicate ETA → escalate if data is insufficient or exception detected.

**Cognitive load:** Low–Medium for standard cases (3–4 structured data points). Judgment calls elevate difficulty: the GPS staleness threshold is an unaided decision; exception flag accuracy requires cross-system awareness; customer frustration signals change the handling approach. Route geography knowledge — "Route 028, last ping Watford 10:48 → ~14:00 estimate" — is non-transferable to a new hire or an agent without this context.

**Zone map:**

| Zone | Conditions | % of Cases | Agent Role |
|---|---|---|---|
| A — Fully agentic | Order found; GPS <30 min; no exception flag | ~65–70% | Respond with ETA; log CRM case |
| B — Agent-led with oversight | GPS 30–60 min stale; minor order match ambiguity | ~20% | Widened estimate + staleness disclosure; flag for supervisor |
| C — Human-led | GPS >60 min; Driver App offline; exception on order; repeat inquiry | ~10% | Escalate with pre-populated context |
| D — Human-only | Active dispute; high-value account; complaint escalation | <5% | Route to account manager; do not intervene |

**Breakpoints:**

| Breakpoint | Consequence if Missed |
|---|---|
| GPS staleness threshold | Agent gives false-precision ETA for a driver who has diverted or stopped |
| Exception flag on order | Agent tells customer delivery is coming; delivery won't happen |
| Repeat inquiry (same customer, same order, 24h) | Agent gives same unhelpful answer twice; customer escalates publicly |
| Order not found after primary lookup | Must attempt secondary (name/address); fail → escalate |

**Hidden work (not in SOP, not in case counts):**
- **Route geography knowledge:** Agent draws on informal map knowledge of driver pacing per route segment. Not documented, not transferable.
- **GPS uncertainty judgement:** Whether a 26-minute-stale ping warrants disclosure, escalation, or a hedged response is an unaided decision. No decision rule exists.
- **Customer frustration signals:** Tone, repetition, "this is the third time I've called" — agents change handling accordingly. Not captured in CRM case fields.
- **Account sensitivity weighting:** Some customers get a tighter answer via informal dispatch call; others get the standard window. This commercial weighting lives in agent memory, not in any system field.

---

### Work Stream 2: Delivery Exceptions (180/day, 12 min avg)

**What actually happens:** Artefact 1 is the textbook case. Driver parked at Stein-Allen, pallet disputed, warehouse operative won't sign, site manager absent, driver has 6 more drops, Sandra's line is busy. Dispatcher must make a disposition decision — hold, return-to-depot, or re-attempt — based on verbal damage description, account knowledge, route schedule awareness, and an insurance protocol that is blank in the SOP.

**Job sequence:** Triage exception type and urgency → assemble context (account tier, consignment value, history, route status) → decide disposition (return/hold/re-attempt/escalate) → instruct driver → notify customer → log and close → flag downstream billing/claims.

**Cognitive load:** High to Very High across all dimensions. Working memory holds driver status + remaining stops + account value + damage description + manager availability + incomplete SOP simultaneously. Pattern recognition ("new warehouse guy won't sign" vs genuine damage) requires domain experience not systematisable without visual confirmation. Dispatcher judgment calls are the irreducible core — no rule covers all cases. Time pressure compounds: every minute parked runs the route schedule.

**Zone map:**

| Zone | Conditions | % of Cognitive Work | Agent Role |
|---|---|---|---|
| A — Fully agentic | None identified | ~0% | No safe fully-agentic path |
| B — Agent support | Triage + context assembly | ~20–25% | Exception type, account, consignment, route context; high-value flag |
| C — Human-led | All disposition and instruction steps | ~65–70% | Surface SOP (staleness warning); account tier; instruction templates |
| D — Human-only | Value >£500; confirmed damage; insurance trigger; Duty Manager escalation | ~10% | Route to Duty Manager |

**Breakpoints:**

| Breakpoint | Consequence if Missed |
|---|---|
| High-value threshold (>£500) | Duty Manager escalation not triggered; decision below authority level |
| SOP incompleteness on damage | No documented anchor; dispatcher has no protocol |
| Insurance protocol trigger | Claims not initiated; evidence window closes |
| Billing implication flag | Billing not notified; customer raises dispute later (Artefact 2 pattern) |
| Driver schedule clock | Route falls behind; downstream deliveries miss windows |

**Hidden work (not in SOP, not in case counts):**
- **Route cascade modelling:** Dispatcher mentally calculates knock-on effect of a delayed driver across remaining stops. Not tracked, not visible in any system.
- **Named-dispatcher personal accountability:** Mark routes specifically to Sandra — not a shared queue. Dispatcher identity is the routing logic. If Sandra is unavailable, exception decision authority breaks with no documented fallback.
- **Relationship weighting:** "Stein-Allen account" is treated as commercially significant. No customer-tier field captures this; weighting lives in dispatcher memory.
- **SOP as operational fiction:** Dispatchers know Section 4.3 doesn't exist and DispatchHub is retired. New hires and AI agents lack this meta-knowledge — both will fail on the same edge cases the team has silently adapted to.
- **Shift-transition orphaning:** In-flight exceptions have no handoff protocol between shifts.

---

### Work Stream 3: Dispatch Adjustments (90/day, 18 min avg)

**What actually happens:** A mid-route change — new pickup, customer divert, driver vehicle issue, weather re-sequence — executed against a Citrix-deployed console with no clean programmatic interface. Artefact 1 shows the dispatcher's mental state during high-pressure events: simultaneously holding route schedules across multiple vehicles and the absence of available decision-makers. Every write action must be executed manually by a human through the desktop UI.

**Job sequence:** Receive and classify adjustment → assess all affected routes and stops → identify 2–3 viable options (reassign/reroute/defer) → execute in Dispatch Console → notify affected drivers via Driver App → log and flag SLA risk.

**Cognitive load:** Very High throughout. Working memory holds 2–4 affected routes simultaneously; changing one recalculates risk across all. Experienced dispatchers know which routes have buffer, which drivers run ahead of schedule, which zones carry traffic risk — none codified. Time pressure is seconds-to-minutes; every minute propagates downstream.

**Zone map:**

| Zone | Conditions | % of Cognitive Work | Agent Role |
|---|---|---|---|
| A — Fully agentic | None — Citrix barrier makes autonomous write execution impossible | ~0% | No safe fully-agentic path |
| B — Agent support | Context assembly before dispatcher acts | ~10–15% | Real-time driver positions, remaining stops, SLA tiers; buffer capacity; high-SLA accounts at risk |
| C — Human-led | All decision and execution steps | ~75–80% | Route maps and stop counts alongside console; driver notification templates |
| D — Human-only | Multi-vehicle re-routing; inevitable SLA breach; high-value account | ~10% | Route to senior dispatcher or ops manager |

**Breakpoints:**

| Breakpoint | Consequence if Missed |
|---|---|
| Multi-vehicle cascade check | Adjusting one route without checking all affected routes → downstream SLA breaches |
| SLA tier awareness | Low-value stop swapped ahead of high-SLA account → contract breach and penalty |
| Driver shift hours / capacity | Extra stops assigned to driver at safe hours limit → compliance risk |
| Citrix write dependency | Any automation attempt → RPA-class failure (same failure mode as prior project) |

**Hidden work (not in SOP, not in case counts):**
- **Buffer capacity knowledge:** Which routes have slack, which drivers run ahead, which zones carry traffic risk — none codified. Re-routing decisions that look arbitrary are informed by weeks of route-level pattern recognition.
- **Multi-vehicle mental model:** Adjusting one route requires holding the state of 2–4 others simultaneously. No system provides this cross-route view; dispatchers assemble it from memory.
- **SLA priority hierarchy:** When two stops cannot both be met, which account absorbs the delay is unwritten commercial knowledge, unenforced by any system field.
- **Shift hours compliance:** Drivers have legal working hour limits. Extra stops cannot be assigned without knowing remaining shift capacity. This information exists in Driver App but is not surfaced in the dispatch decision flow.

---

### Work Stream 4: Billing Disputes (60/day, 28 min avg)

**What actually happens:** Artefact 2 directly. Hayes & Sons disputes INV-2026-04318 over a fuel surcharge. Sandra looks up the invoice in Aurum, cross-references the surcharge calculation, and applies a £170 goodwill credit via manual workaround — bypassing APPROVER_ID + AUDIT_REF entirely. APEX_DISPUTES_OPEN shows D-2026-00342 still PENDING_CLAIM: credit did not close the record. Hayes & Sons (C-04451) has 3 FUEL_SURCH_DAMAGE disputes in 2026.

The 28-minute handling time almost certainly includes Aurum loading time, legacy screen navigation, manual CSV cross-referencing, and drafting a customer response. Active decision-making is probably 5–8 minutes. The rest is system friction — which is the critical distinction: AERA cannot speed up Aurum, but it can eliminate almost all retrieval and cross-referencing time.

**Job sequence:** Parse and classify dispute → retrieve invoice, surcharge, credit history from T-1 batch → validate the claim → determine resolution (credit/rejection/escalation) → execute via APPROVER_ID + AUDIT_REF staging or draft rejection → communicate outcome → log and flag repeat pattern.

**Cognitive load:** Medium. Invoice, surcharge, credit history, account tier, and credit authority limits are manageable because data is structured and retrievable. Key judgment calls: goodwill vs calculation-error correction are different decisions; Hayes & Sons' repeat pattern may be a pricing model conversation, not a dispute resolution. High context dependency on account tier and prior dispute history.

**Zone map:**

| Zone | Conditions | % of Cognitive Work | Agent Role |
|---|---|---|---|
| A — Fully agentic | None — Aurum batch-only means no real-time credit application | 0% | Not achievable without live Aurum API |
| B — Agent support | Triage, data retrieval, claim validation, response drafting | ~30–35% | Classify dispute; pull Aurum data package; validate surcharge arithmetic; detect repeat patterns; draft response for human review |
| C — Human-led | Resolution decision and credit approval | ~55–60% | Surface credit authority thresholds; pre-populate APPROVER_ID + AUDIT_REF staging; block manual override |
| D — Human-only | High-value disputes; legal/contract implications; account churn risk | ~10% | Route to account manager or finance lead |

**Breakpoints:**

| Breakpoint | Consequence if Missed |
|---|---|
| Credit authority threshold | Credit applied without APPROVER_ID → audit trail failure (already happening — Artefact 2) |
| T-1 data lag disclosure | Response based on yesterday's batch when today's data is absent → factual error in customer communication |
| Dispute record closure | Credit applied but dispute not updated → appears unresolved; customer re-raises (Artefact 2 pattern) |
| Repeat pattern detection | Hayes & Sons treated as isolated incidents → systemic account issue and root cause never addressed |

**Hidden work (not in SOP, not in case counts):**
- **Aurum workaround knowledge:** The formal 48-hour Aurum ticket path is avoided; goodwill credit via manual override is the actual resolution path for time-sensitive disputes. Tribal knowledge — not documented, not onboarded.
- **Credit authority ambiguity:** Sandra applied £170 via manual override. Whether this is within documented authority is unknown. Agents exercise undocumented credit discretion on every case.
- **Cross-system pattern detection:** "Second time this quarter" (Artefact 2) is agent memory, not a system alert. Hayes & Sons has 3 disputes in 7 weeks — no flag, no escalation. Pattern recognition lives in individual agent memory; no mechanism for a different agent to inherit this context.
- **Audit log bypass as informal norm:** The formal APPROVER_ID + AUDIT_REF pathway exists but is bypassed. Agents experience it as a speed optimisation; they may not know it creates compliance exposure.
- **Channel confusion:** Billing disputes often arrive at billing@ (Aurum Billing Team) and get re-routed to Customer Ops — adding a structural one-day delay before any action begins.

---

## Operational Memory Fragmentation

Apex's operational continuity depends on human-held knowledge that no system captures. Human operators are the orchestration layer — not because systems are absent, but because systems do not capture the context required to coordinate work across incomplete process definitions, legacy constraints, and relationship-sensitive decisions.

| Pattern | Observed In | Risk |
|---|---|---|
| Named-dispatcher routing | Artefact 1: Mark routes to Sandra specifically, not shared queue | Single point of failure; no documented handoff; shift transitions orphan in-flight cases |
| Manual credit workaround | Artefact 2: Sandra's goodwill credit bypasses APPROVER_ID pathway | Tribal knowledge; compliance risk; not replicable by agent without audit trail |
| SOP as operational fiction | SOP v2.3: DispatchHub retired; Section 4.3 blank | Agents operate on meta-knowledge that the SOP is wrong — invisible to new hires and agents built against it |
| Repeat dispute blindness | Artefact 2 + Gate 2 Artifacts: Hayes & Sons 3 disputes in 7 weeks, no alert | Pattern recognition lives in individual agent memory; no cross-case visibility |
| Commercial account weighting | Artefact 1: Stein-Allen treated as high-value by dispatcher judgment | Weighting not encoded in any system field; uniform agent handling eliminates differentiation |

This is why orchestration support is prioritised over autonomous replacement: externalising fragmented operational context into observable, auditable system state is the prerequisite for safe delegation. AERA externalises a narrow, defined slice of this context first.

---

**Cross-stream causality:** An unresolved delivery exception triggers a cascade through the entire function. The affected route generates an ETA inquiry spike. If the exception involves damage, a billing dispute follows 1–9 days later — Artefact 2 (Hayes & Sons) is downstream of exactly this chain. If the billing dispute is mishandled, account degradation follows. This is why delivery exceptions carry the highest long-term orchestration leverage despite being only 25% of daily volume. Compressing ETA inquiry volume has secondary strategic value during exception surges — freeing agent attention at the exact moment exception demand peaks.

**Peak-load and surge behaviour:** Daily averages mask operational burst patterns intrinsic to logistics. Route failures, weather disruptions, and failed-delivery surges drive ETA and exception volumes significantly above daily averages during the same 30–60 minute window. Pilot measurement must capture peak-load behaviour before drawing conclusions about agent handling capacity or compression ceilings.

**Context assembly:** All four work streams require CRM context assembly before action. ETA: 3–4 data points, simple lookup. Billing: 6–7 structured items from Aurum batch + CRM. Dispatch: real-time multi-route state across 2–4 drivers. Exceptions: 6–8 data points including unstructured verbal input and incomplete SOP. A shared context-assembly layer is viable in principle; the ETA agent is the right place to build and prove this pattern.

---

## Deliverable 2 — Delegation Suitability Matrix

**Scoring method:** Six dimensions, 1–5 scale. Three dimensions are inverse-scored (INV): higher = harder to automate. Automation readiness = average of adjusted scores.

| Dimension | 1 | 5 |
|---|---|---|
| Repeatability | Highly variable | Fully rule-based |
| Data availability | Not available / batch-only | Real-time API |
| Error consequence (INV) | Trivial | Catastrophic |
| Time pressure | Days / no urgency | Seconds-critical |
| Judgment required (INV) | Fully rule-based | Irreducible human judgment |
| Regulatory / compliance (INV) | None | High obligation |

### ETA Inquiries — 4.2 / 5 — Agent-led with oversight

| Dimension | Raw | Adjusted | Notes |
|---|---|---|---|
| Repeatability | 5 | 5 | Structured lookup: order ID → route → GPS → window → respond |
| Data availability | 4 | 4 | CRM REST API confirmed; Driver App API assumed (not confirmed) |
| Error consequence (INV) | 2 | **4** | ETA slightly off = minor frustration; not financially consequential |
| Time pressure | 3 | 3 | Quick response expected; not seconds-critical |
| Judgment required (INV) | 2 | **4** | Standard case is lookup-only; edge cases use threshold rules |
| Regulatory (INV) | 1 | **5** | No compliance obligation |

Rationale: Zone A (~65–70%) is fully automatable. Does not earn "fully agentic" because Driver App API is assumed not confirmed, and GPS staleness creates unavoidable edge conditions requiring human fallback. "Fully agentic" is the right long-term destination once both are validated in production.

---

### Delivery Exceptions — 2.5 / 5 — Human-led with agent support

| Dimension | Raw | Adjusted | Notes |
|---|---|---|---|
| Repeatability | 2 | 2 | Highly variable: damage, refusal, unattended, high-value. SOP incomplete. |
| Data availability | 3 | 3 | CRM available; Driver App partial; damage protocol absent |
| Error consequence (INV) | 4 | **2** | Wrong call = driver stranded, customer lost, insurance gap, SLA breach |
| Time pressure | 4 | 4 | Driver waiting; route schedule running |
| Judgment required (INV) | 5 | **1** | Dispatcher discretion IS the core; not substitutable |
| Regulatory (INV) | 3 | **3** | Insurance protocol involved; SOP gap |

Rationale: Artefact 1 makes concrete what the scores reflect — the decision cannot be made from data alone. Agent role is triage and context assembly (JTBD-EX-1, EX-2) only. Assigning this as "agent-led" would expose Apex to operational failure on the highest-stakes cases.

---

### Dispatch Adjustments — 2.8 / 5 — Human-led with agent support

| Dimension | Raw | Adjusted | Notes |
|---|---|---|---|
| Repeatability | 3 | 3 | Structured parameters; highly contextual execution |
| Data availability | 2 | 2 | Dispatch Console is Citrix — no clean API |
| Error consequence (INV) | 5 | **1** | Wrong adjustment = multi-vehicle cascade, SLA breach |
| Time pressure | 5 | 5 | Mid-route; seconds-to-minutes decision window |
| Judgment required (INV) | 4 | **2** | Route knowledge, driver capacity, traffic — significant expertise |
| Regulatory (INV) | 2 | **4** | Contractual SLA obligations |

Rationale: Hard technical constraint — Citrix has no clean API. Any automated write access is RPA-class, same failure mode as prior project. This work stream becomes more agentic only after Dispatch Console re-platforming — a separate multi-year project.

---

### Billing Disputes — 2.3 / 5 — Human-led with agent support

| Dimension | Raw | Adjusted | Notes |
|---|---|---|---|
| Repeatability | 3 | 3 | Dispute types categorisable; resolution is not |
| Data availability | 2 | 2 | Aurum batch-only; T-1 lag; no real-time |
| Error consequence (INV) | 3 | **3** | Incorrect credit = P&L impact; missed credit = customer attrition |
| Time pressure | 1 | 1 | Resolved over days; no urgency |
| Judgment required (INV) | 3 | **3** | Policy interpretation + account relationship + credit authority |
| Regulatory (INV) | 4 | **2** | Audit trail required; credit bypass pattern observed (Artefact 2) |

Rationale: Aurum's batch-only architecture is a hard ceiling. The audit trail gap adds governance risk — an agent operating here without enforced audit controls would compound an existing failure. Agent role: parse dispute type, surface T-1 data, draft factual response, stage credit for human approval via formal APPROVER_ID + AUDIT_REF pathway only.

---

### Summary

| Work Stream | Volume/Day | Readiness | Archetype | Primary Constraint |
|---|---|---|---|---|
| ETA Inquiries | 400 | **4.2 / 5** | **Agent-led with oversight** | Driver App API confirmation; GPS staleness handling |
| Delivery Exceptions | 180 | 2.5 / 5 | Human-led with agent support | Dispatcher judgment irreducible; SOP incomplete |
| Dispatch Adjustments | 90 | 2.8 / 5 | Human-led with agent support | Citrix integration barrier; high error consequence |
| Billing Disputes | 60 | 2.3 / 5 | Human-led with agent support | Aurum batch-only hard ceiling; audit trail gap |

**Anti-pattern note:** Both prior Apex automation failures (chatbot, RPA billing) were over-scoped relative to actual system and human-judgment constraints. This matrix is intentionally conservative. "Everything is fully agentic" is precisely the failure mode Apex has already lived through twice.

---

## Deliverable 3 — Volume × Value Analysis

**Value metric:** Daily minutes × automatable fraction × data quality, discounted by risk. Value is the intersection of effort, automation ceiling, and risk — not raw case volume.

| Work Stream | Volume/Day | Daily Minutes | Automatable % | Mins Recoverable | Data Quality | Risk |
|---|---|---|---|---|---|---|
| ETA Inquiries | **400** | 1,600 | **~70%** | **~1,120** | High | Low |
| Delivery Exceptions | 180 | 2,160 | ~25% | ~540 | Medium | High |
| Billing Disputes | 60 | 1,680 | ~35% | ~588 | Low | High |
| Dispatch Adjustments | 90 | 1,620 | ~15% | ~243 | Low | Very High |

**Staffing model interpretation:** The modelled load (~117.7 hrs/day) covers only four documented work streams and does not explain the full 35-person headcount. The gap reflects hidden coordination work not captured in case counts, multitasking fragmentation, shift coverage overhead, supervisory load, and informal coordination (the named-dispatcher dynamic in Artefact 1 is load that appears in no case count). No conclusions about team underutilisation should be drawn from this model. The unmodelled work is real operational load.

**Blast radius comparison — why ETA was selected over higher-value opportunities:**

| Opportunity | Error Scenario | Blast Radius | Reversibility |
|---|---|---|---|
| ETA inquiry — wrong window | Customer receives inaccurate ETA | **Low** — correctable with follow-up; no system state changed | **High** |
| Exception disposition — wrong call | Driver returns unnecessarily; route delayed; customer complaint; re-delivery cost | **High** — cascades to route, depot, customer, billing | **Low** |
| Billing dispute — wrong credit | Unauthorised credit; audit trail gap; potential CFO-level exposure | **High** — financial and compliance consequences | **Low** |
| Dispatch adjustment — wrong routing | Delivery failure; SLA breach; driver safety risk | **Very High** — irreversible within shift window | **None** |

ETA inquiry is the only work stream where an agent error is operationally recoverable and financially contained. MVP selection considered blast radius, not only savings.

### Primary Target: ETA Inquiries

**Why it wins:** 400 cases/day at ~70% automatable = ~1,120 recoverable person-minutes/day. Salesforce CRM has a confirmed REST API. Driver App GPS is an API confirmation question, not a system rebuild. A wrong ETA estimate is recoverable — contrasting with exceptions (operational failure), adjustments (multi-vehicle cascade), and billing (financial impact + audit). An ETA agent is immediately demonstrable, does not touch Aurum, and does not require Citrix integration. Sarah Whitmore needs a result visibly different from the prior chatbot failure.

**Estimated impact:**
- ~1,120 recoverable person-minutes/day ≈ 18.7 person-hours/day ≈ **2.5 FTE-equivalent capacity** annualised (48 weeks × 5 days)
- Fully-loaded agent cost ~£33,000/year (salary ~£26,000 + employer NI ~£2,300 + pension ~£780 + 15% overhead ~£3,900) → **~£82,500/year in released capacity value**
- *Caveats:* Released capacity, not guaranteed cash savings. Intended for redeployment into higher-judgment work, not headcount reduction. The CEO's £1.2M competitor benchmark reflects a multi-year, multi-work-stream deployment — not a comparable starting point for an organisation recovering from two automation failures.

**What the MVP validates, not delivers:** Do confidence-calibrated ETA responses work under live conditions? Is the Driver App GPS API reliable enough to build against? Will agents accept agent-handled cases or route around them? Are escalation thresholds correctly calibrated? These signals are the prerequisite for any larger investment. The full phased programme (Phases 1–3) might reach £200,000–300,000/year — still below £1.2M, because Apex's system maturity caps near-term automation. See D6 Q9 for how to surface this gap constructively.

### Secondary Target: Billing Dispute Triage

Hayes & Sons (C-04451) alone has 3 FUEL_SURCH_DAMAGE disputes open in 2026. Agent role: parse dispute, retrieve T-1 data, cross-reference APEX_DISPUTES_OPEN, draft factual response, stage credit for human approval via formal pathway. **Prerequisite:** Fix the audit trail governance issue before any billing agent work. Automating on a broken audit trail compounds the control failure.

### Phased Sequencing

| Phase | Target | Dependencies | Readiness |
|---|---|---|---|
| **Phase 1** | ETA Inquiries Agent | Driver App API confirmed; Salesforce schema | **Now** |
| **Phase 2** | Billing Dispute Triage | Audit trail governance fixed; Aurum batch pipeline | After Phase 1 stable |
| **Phase 3** | Exception Context Assembly | SOP updated; insurance protocol documented | After Phase 2 |
| **Phase 4** | Dispatch Adjustments | Dispatch Console API re-platform | Multi-year; separate project |

---

## Deliverable 4 — Agent Purpose Document

**Work stream:** ETA Inquiries (Phase 1) — **Agent-led with oversight**

### Purpose Statement

The Apex ETA Agent resolves inbound "where is my delivery?" inquiries by retrieving the delivery's route assignment and GPS-derived position from Salesforce CRM and the Driver App, interpreting timing with confidence calibration, and either responding directly or escalating to a human dispatcher when data is insufficient or an exception state is detected.

It does not make operational decisions. It does not touch billing. It answers one question: *when will my delivery arrive?*

### Scope

**In scope:** ETA inquiries via SMS, email, and (if confirmed) web portal. Order identification. Route and GPS data retrieval. Confidence-calibrated ETA response. CRM case logging. Escalation routing with pre-populated context.

**Out of scope:**

| Excluded | Reason |
|---|---|
| Delivery exceptions | Dispatcher judgment required |
| Dispatch adjustments | Citrix integration barrier |
| Billing disputes | Aurum constraint; separate project |
| Credit, refund, or goodwill decisions | Never in scope for this agent |
| Complaints handling | Human-only |

### KPIs

| KPI | Target | Measurement |
|---|---|---|
| First-contact resolution | ≥ 85% without human handoff | CRM case closure flag |
| Avg response time | < 2 min (vs ~4 min current) | CRM timestamp delta |
| Escalation rate | < 20% | Escalations / total ETA cases |
| GPS-stale escalations | < 10% of total | Agent audit log: staleness trigger events |
| Customer satisfaction | ≥ current baseline | Post-interaction survey (baseline = discovery question) |
| False precision errors | 0 | Audit: responses with GPS data >60 min stale |

### ETA Confidence Tier Definition

Confidence tier is a structured uncertainty signal — not a precise probability. It controls customer-facing language and determines whether a human review flag is raised.

| Tier | Conditions | Customer-Facing Language |
|---|---|---|
| **Tier 1 — Moderate confidence** | GPS ≤30 min; no exception flag | "Your delivery is currently estimated to arrive between [window]. Our last tracking update was [X] minutes ago." |
| **Tier 2 — Low confidence** | GPS 30–60 min; no exception flag | "Your delivery is estimated to arrive [window], though our tracking is [X] minutes old. We'll update you if anything changes significantly." |
| **Tier 3 — Insufficient data** | GPS >60 min; exception flag active; Driver App unreachable | Escalate. No ETA sent to customer. Agent handles. |

Even Tier 1 responses carry uncertainty: fresh GPS confirms a driver's last known location but does not capture route reprioritisation, failed prior drops, parking delays, or driver discretion on stop sequence. Tier 1 language uses window estimates, not point-in-time precision.

### Autonomy Matrix

| Mode | Conditions | Agent Action | Human Role |
|---|---|---|---|
| **Autonomous** | Order found; GPS <30 min (Tier 1); no exception flag | Respond with ETA; log CRM case | Passive monitoring |
| **Supervised** | GPS 30–60 min (Tier 2); no exception flag | Widened window + staleness disclosure; flag for supervisor | May override; not required |
| **Escalate → Dispatcher** | GPS >60 min (Tier 3); Driver App unreachable; exception state; order not found after secondary | Pre-populate context; tell customer they'll receive an update | Dispatcher responds |
| **Escalate → Human Agent** | >1 inquiry same order/24h; complaint language; active billing dispute; strategic account | Route to human agent | Human owns interaction |

**Principle: when mode is ambiguous, escalate. Never infer. Never guess.**

### Escalation Triggers (complete)

1. GPS ping >60 minutes old
2. Driver App API unreachable or returning errors
3. Order exception flag in CRM or Driver App (any type)
4. Order not found after primary AND secondary lookup
5. Same customer, same order, >1 inquiry within 24 hours
6. Explicit escalation or complaint language from customer
7. Open dispute record in APEX_DISPUTES_OPEN for this order
8. Delivery status = "complete" but no scan-on-delivery event (potential missing parcel)
9. Customer identified as strategic account — `[VALIDATED — Gate 2 Artifacts]` ACCT_MGR field confirmed in APEX_CUSTOMER_MASTER. Route where CUSTOMER_ID maps to a named ACCT_MGR (e.g., U-0089 for Hayes & Sons, Severn Wholesale, Travis & Mason) to that agent's named queue. Uniform agent responses for named-account customers carry reputational and contractual risk that does not appear in individual-case blast-radius calculations. **Build-ready.**

### Activity Catalogue

| Step | Activity | System | Mode |
|---|---|---|---|
| 1 | Parse inbound message; extract order reference | Comms gateway | Autonomous |
| 2 | Primary CRM lookup: order ID → customer → delivery record | Salesforce CRM | Autonomous |
| 3 | Secondary CRM lookup: name + delivery address | Salesforce CRM | Autonomous |
| 4 | Pull route assignment from delivery record | Salesforce CRM | Autonomous |
| 5 | Query Driver App: GPS last ping, delivery sequence, exception flags | Driver App (REST — assumed) | Autonomous |
| 6 | Evaluate GPS staleness | Internal rules | Autonomous |
| 7 | Check exception flags (CRM + Driver App) | CRM + Driver App | Autonomous |
| 8 | Cross-reference APEX_DISPUTES_OPEN (T-1 batch) | Daily ingested CSV | Autonomous |
| 9 | Apply autonomy matrix → determine mode | Internal rules engine | Autonomous |
| 10 | Compose response or prepare escalation context | Comms gateway / CRM | Autonomous / Supervised |
| 11 | Send response or route escalation with context | Comms gateway / CRM | Autonomous / Human |
| 12 | Log CRM case (channel, query, mode, response, GPS age, flags) | Salesforce CRM | Autonomous |

### Failure Modes and Mitigations

| Failure | Likelihood | Impact | Mitigation |
|---|---|---|---|
| GPS stale (rural / tunnel coverage) | Medium | High | Hard staleness thresholds. Never extrapolate GPS position. |
| Exception in Driver App not yet in CRM | Medium | High | Check both sources; discrepancy → escalate |
| Multiple orders for B2B customer | Medium | Low | Secondary lookup by invoice/address; escalate if ambiguous |
| Driver App offline | Low | High | Any API error → immediate escalation; no cached stale GPS fallback |
| Delivery complete in CRM but parcel missing | Low | Very High | Only confirm delivery with scan-on-delivery event present |
| APEX_DISPUTES_OPEN batch missing | Low | Medium | Log warning; treat dispute flag as unknown; escalate billing-adjacent queries |

### Pilot Governance Model

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

### KPI Gaming Risks

| Risk | Mechanism | Mitigation |
|---|---|---|
| Rubber-stamped escalations | Agents nominally review but functionally accept AERA outputs — oversight becomes illusory | 10% weekly qualitative case sampling on decision quality, not only escalation accuracy |
| Handling-time deflation | Agents speed-process under measurement pressure to inflate time-freed KPI | Track decision quality and re-contact rate on escalated cases separately from throughput |
| ETA window widening | Dispatchers extend windows to reduce false-precision complaint rate | Track nominal delivery window width as a secondary trend signal across the pilot |
| Escalation gaming | Agents inflate or suppress escalations to affect KPI narrative | Escalation rate is a calibration input, not a success metric — interpret only with re-contact rate and decision quality |

Quantitative KPIs require a parallel qualitative review programme — weekly 10% case sampling, bi-weekly dispatcher sentiment check-ins, monthly handling-pattern audit.

---

### Organisational Rejection Risks

| Risk | Mechanism | Mitigation |
|---|---|---|
| Dispatcher ownership resistance | Named-dispatcher routing creates implicit route ownership; shared agent queue perceived as depersonalising accountability | Co-design queue architecture with dispatchers before build; exception pre-assembly must route to named dispatcher, not generic pool |
| Bypass behaviour | Agents who distrust AERA's confidence tiers handle ETA cases manually, negating compression value | Monitor handling rate split weekly; treat systematic bypass as threshold miscalibration signal, not a discipline problem |
| Trust erosion from false precision | A sequence of wrong ETAs causes the team to lose confidence in all AERA outputs; trust erodes asymmetrically | Surface weekly error analysis visibly to the team; do not obscure incorrect estimates |
| Judgment displacement anxiety | Agents or dispatchers fear AERA expansion into exception classification | Communicate APD scope split explicitly at launch: MVP scope / Pilot scope / Future scope (blocked with named prerequisites) |
| Surveillance perception | GPS logging perceived by drivers as individual performance monitoring | Frame AERA as team capacity tool; GPS data scoped to ETA estimation only — not accessible for driver performance evaluation |

**Adoption failure is a first-class risk.** A technically correct AERA deployment that dispatchers bypass is operationally equivalent to a failed deployment — and may be harder to recover from as the third failed automation initiative.

---

### Secondary Build Scope: Exception Context Pre-Assembly

*(Build-ready; Phase 1b — deploy alongside or immediately after AERA pilot. Shares Salesforce + Driver App API surface.)*

On exception case creation in Salesforce, automatically populate: customer record and account flags, order history, prior exception cases, consignment value with >£500 Duty Manager escalation flag, and current GPS status for the assigned driver.

**In scope:** Pre-assembled context panel in Salesforce case view before dispatcher action.  
**Out of scope:** Exception classification, disposition recommendation, driver/depot communication, any routing decision.  
**Critical dependency:** Named-dispatcher routing model must be confirmed (D6 Q7). If dispatchers hold named-route ownership, exception context must surface in the named dispatcher's queue — not a generic pool.

---

### Build Instruction

Start with: Activity steps 1–4 (parse → CRM lookup → route retrieval). These depend only on the confirmed Salesforce CRM API. Do not begin GPS integration (steps 5–8) until Driver App API spec is confirmed by the Driver App team. See [CLAUDE.md](CLAUDE.md) for full coding constraints.

---

## Deliverable 5 — System / Data Inventory

### System Detail

**Salesforce CRM**

| Attribute | Status |
|---|---|
| Integration surface | REST API confirmed |
| ETA agent needs | Order → delivery → route; customer profile; case write; exception flag |
| Exception agent needs | Account tier, credit limit, contract type, prior exception history |
| Billing agent needs | Case history, prior dispute records |
| Known gaps | Schema field names unknown; route_code linkage to Driver App assumed; API rate limits unknown |
| Risk | Low |
| Key assumption | CRM delivery record contains route_code linking to Driver App (Confidence: **Medium**) |

**Driver App (in-house iOS/Android)**

| Attribute | Status |
|---|---|
| Integration surface | **Unknown — no API spec in brief** |
| ETA agent needs | GPS last ping (timestamp + coordinates), delivery sequence, exception flags, scan-on-delivery events |
| Known gaps | API existence unconfirmed; GPS refresh cadence unknown; 26-min stale observed in production |
| Risk | **Medium-High — critical gap** |
| Key assumptions | Backend exposes REST API (Confidence: **Medium**); GPS refreshes every 5–10 min normally (Confidence: **Low**) |
| Blocking item | Do not build GPS integration until API spec confirmed |

**Dispatch Console (Java/Citrix)**

| Attribute | Status |
|---|---|
| Integration surface | "Limited API surface" — Citrix-deployed |
| Integration barrier | Citrix = RPA-class integration only (brittle; same failure mode as prior project) |
| Risk | **High** |
| Recommendation | Do not attempt Dispatch Console integration in Phase 1 or 2. Gate on re-platform decision. |

**Aurum Billing (on-prem Oracle, 2008)**

| Attribute | Status |
|---|---|
| Integration surface | **Batch CSV only** |
| Not available | Real-time lookup, real-time credit application, line-item adjustment |
| Invoice modification | Manual Aurum support ticket; 48h typical turnaround |
| Schema stability | Changes ~quarterly without notice — killed prior RPA project |
| Credit audit gap | Sandra's £170 absent from APEX_CREDITS; formal pathway bypassed (intermittently confirmed by Gate 2 Artifacts) |
| Risk | **Critical** |

**Aurum mitigations (required before any billing agent work):**
1. Hash-compare CSV headers on every import; alert on any change before processing
2. Ingest daily batch at 04:30 GMT into internal queryable database; agent queries this layer, never raw CSV
3. All responses using Aurum data must disclose "as of [yesterday's date]"
4. Agent may propose credits only — always via APPROVER_ID + AUDIT_REF pathway; block manual override pattern
5. When invoice modification is required, communicate the 48h turnaround to the customer immediately

### Data Availability Matrix

| Data Item | Source | Available? | Latency | Risk |
|---|---|---|---|---|
| Order → customer record | Salesforce CRM | Yes (API) | Real-time | Low |
| Order → route assignment | Salesforce CRM | Yes (assumed schema) | Real-time | Medium |
| Route → driver → GPS ping | Driver App | Assumed | Real-time (assumed) | **High** |
| GPS ping timestamp | Driver App | Assumed | Real-time (assumed) | **High** |
| Exception flag on delivery | CRM + Driver App | Partial | CRM real-time; Driver App assumed | Medium |
| Scan-on-delivery event | Driver App | Assumed | Real-time (assumed) | Medium |
| Invoice data | Aurum batch | Yes (CSV) | T-1 | Medium |
| Fuel surcharge breakdown | Aurum batch | Yes (CSV) | T-1 | Medium |
| Credit history | Aurum batch | Yes (CSV) — with bypass gap | T-1 | **High** |
| Open disputes | Aurum batch | Yes (CSV) | T-1 | Medium |
| Customer master | Aurum batch | Yes (CSV) | Monthly | Low |

### Assumptions Register

| # | Assumption | Confidence | How to Test |
|---|---|---|---|
| A1 | Driver App backend exposes REST API | **Medium** | Architecture review with Driver App team |
| A2 | GPS refreshes every 5–10 min under normal conditions | **Low** (Artefact 3 contradicts) | GPS lag histogram from Driver App logs |
| A3 | CRM delivery record contains route_code linking to Driver App | **Medium** | Salesforce schema review |
| A4 | 400 ETA inquiries/day includes SMS + email + possibly web | **Low** | CRM case source field analytics |
| A5 | Salesforce API rate limits not a constraint at 400 cases/day | **Low** | Confirm Salesforce license tier with IT |
| A6 | Customer-facing web portal or tracking page exists | **Low** | Confirm with Sarah |
| A7 | Driver App exception flags propagate to CRM in near-real-time | **Medium** | Test: create exception in Driver App; observe CRM lag |
| A8 | Dispatcher has defined SLA for escalated ETA responses | **Low** | Operational question for Sarah |
| A9 | Aurum has no read API beyond batch exports | **High** (brief explicit; prior project confirms) | Confirm with Aurum support as formality |
| A10 | Dispatch Console "limited API" means no write access | **High** | Technical spike with IT |

### Risk Summary

| Item | Risk Type | Impact if Wrong |
|---|---|---|
| Driver App API availability | Integration risk | GPS integration blocked; ETA agent limited to 4-hour window only |
| GPS refresh cadence | Data quality risk | More frequent false-precision escalations than planned |
| Aurum schema changes | Fragility risk | Billing triage agent breaks silently on next quarterly change |
| Credit audit bypass pattern | Governance risk | Billing agent built on compromised audit trail; financial control gap widens |
| SOP 4.3 incompleteness | Process risk | Exception context assembly has no rule set for damage cases |
| Citrix integration barrier | Technical risk | Dispatch adjustment automation fails as prior RPA project did |

### Shadow Systems and Undocumented Dependencies

| Shadow System | Observed In | Risk |
|---|---|---|
| Named-dispatcher personal queues | Artefact 1: Mark routes specifically to Sandra, not shared dispatch line | **High** — single point of failure; no documented handoff; any agent queue design must account for named routing expectations or dispatchers will ignore the queue |
| Tribal knowledge: Aurum goodwill credit workaround | Artefact 2: Sandra's resolution method — manual override, unstated authority | **High** — undocumented; compliance risk; credit authority ceiling unknown; not replicable by agent without audit trail |
| Credits audit log bypass | Artefact 2 internal note; `[VALIDATED]` APEX_CREDITS confirms intermittent failure | **Critical** — agent must not replicate. Any agent output touching credits must be logged in Salesforce, not only in Aurum. The Aurum credits CSV cannot be relied upon as a complete record. |
| Informal customer pattern awareness | Artefact 2: "second time this quarter" — `[VALIDATED]` Hayes & Sons (C-04451) has 3 open disputes in 7 weeks, all assigned to Sandra W. | Agent opportunity via Salesforce history — observable via repeat dispute flag. **MVP value confirmed.** |

### Missing Systems / Blocked Integrations

| Gap | Impact on Design | Resolution Path |
|---|---|---|
| Aurum real-time API | Billing dispute resolution blocked; structural T-1 lag | Long-term: Aurum replacement or real-time middleware. Short-term: batch context pre-assembly with explicit lag caveat and schema-diff monitoring as prerequisite. |
| Dispatch Console API undefined | Exception decision support blocked; dispatch adjustment orchestration blocked | Engineering discovery sprint required. Treat as blocked until API scope confirmed in writing. |
| Cross-case linkage (exception ↔ billing dispute) | Same-consignment disputes require manual cross-reference across two Salesforce records | Short-term: Salesforce custom field linking exception case to billing dispute case, populated manually at intake. Longer-term: automated match on shared order number at case creation. |
| SOP knowledge base (current) | SOP v2.3 cannot be used for agent decision logic — references retired tools, incomplete damage protocol | Prerequisite: SOP revised and signed off by Sarah Whitmore. Human process dependency, not technical. |

---

## Deliverable 6 — Discovery Questions

*Questions whose answers would materially change the design. Tied to specific tensions in the artefacts and brief.*

### Tier 1: Design-Blocking

**Q1 — Driver App API**
> *"The ETA agent depends on querying the Driver App for GPS data. The brief says the app is in-house. Does the backend expose an API that other systems can query, or does the dispatch team interact with it only through the web console? If there's no API, the GPS integration phase has no foundation — I need to know before we scope the build."*

Changes if no API: Phase 1 limited to CRM-only ETA (4-hour standard window only); precision-narrowing value proposition is unavailable until a Driver App API is built.  
Evasion signal: "I'd have to ask IT." → Press: "Can I speak with the tech lead for 30 minutes? The whole GPS phase depends on this."

---

**Q2 — What made the chatbot fail**
> *"You mentioned the 2024 chatbot customers hated. Was it the channel (customers didn't want a bot), the answer quality (wrong or useless answers), or the scope (tried to handle too much)? I'm asking because the ETA agent has surface similarity to a chatbot and I need to design against the right failure mode."*

Changes: Channel aversion → visible escape hatch from first contact. Answer quality → staleness thresholds are the key safeguard. Scope → narrow scope (ETA only) is the differentiator to emphasise.  
Evasion signal: "It just wasn't good." → "Did customers complain about talking to a bot, or about the answers they received? Those are different problems."

---

**Q3 — Credits audit trail and approval authority**
> *"The Artefact 2 internal note says Sandra applied a £170 credit with no entry in the credits audit log. How common is this — and who has authority to approve a credit above, say, £100?"*

Changes: If bypasses are routine, a billing agent using the formal pathway will conflict with current practice. The answer determines whether Phase 2 is a "build the agent" or "fix governance first" problem.

`[VALIDATED — Gate 2 Artifacts]` APEX_CREDITS_20260414.csv confirms proper audit structure for some credits (CR-2026-00814, Hayes & Sons £88, APPROVER_ID U-0089). The bypass is intermittent — some credits properly logged, others bypass audit trail unpredictably. Q3 has changed from "is the audit trail broken?" to "when does it break, and who decides?"  
Evasion: "That was a one-off." → "C-04451 has three FUEL_SURCH_DAMAGE disputes and a prior goodwill credit for the same customer. Is this specifically Sandra or a broader pattern?"

---

**Q4 — GPS lag in production**
> *"The SMS artefact shows a 26-minute GPS lag. Is that typical or unusual? I need the realistic GPS latency to set the right staleness thresholds — if 26 minutes is normal, my 30-minute threshold will escalate 30–40% of cases rather than the planned 20%."*

Evasion: "It varies." → "In a typical day, what fraction of ETA inquiries require an agent to call dispatch because the GPS window is too wide? Even a rough guess helps."

---

### Tier 2: Scope-Defining

**Q5 — ETA inquiry channel breakdown**
> *"The 400/day figure doesn't show channel split. Roughly what proportion are SMS, email, phone, and web (if you have a portal)? Build scope changes significantly for two channels versus four."*

**Q6 — Billing disputes: active time vs elapsed time**
> *"Does the 28-minute handling time represent active agent work, or elapsed time including waiting for Aurum to load, callbacks, or approval? If it's 5 minutes active work + 23 minutes waiting, the automation opportunity is very different."*

**Q7 — Sandra's authority and team structure**
> *"Sandra appears to handle a disproportionate share of billing disputes and exception cases. Is exception handling and billing dispute work concentrated in a few named specialists, or distributed across the team? And is the Duty Manager role actively staffed on each shift?"*

**Q8 — SOP gap**
> *"Section 4.3 — damaged consignments — is blank, marked 'TBD.' The SOP still references DispatchHub, retired in 2024. Is an SOP rewrite in progress, or is the team operating on informal knowledge for damage handling?"*

**Q9 — Competitor context**
> *"Your CEO mentioned a competitor saving £1.2M on AI. Do you know what they actually changed — inbound volume reduction, headcount redeployment, something else? I'm asking because that number will come up in your internal approvals and I want the ROI framing to be defensible."*

---

### Tier 3: Constraint-Validating

**Q10 — Contractual SLAs and breach tracking**
> *"Are there contractual SLAs with B2B customers governing exception resolution or billing dispute turnaround times? The Hayes & Sons thread shows 9 days between initial contact and resolution — is that a breach, and is breach status tracked in Salesforce or Aurum?"*

Changes if tracked in Salesforce: SLA breach flag becomes a priority signal in exception context pre-assembly — cases near or past breach route differently. If SLAs exist but are untracked: SLA tracking becomes a prerequisite for priority-weighted escalation design. If SLAs don't exist: the Hayes & Sons pattern is a relationship management issue, not a compliance one, changing escalation urgency framing.

**Q11 — Salesforce customer-tier or key-account flag**
> *"Does Salesforce carry a customer-tier, key-account, or commercial-sensitivity flag? The Stein-Allen account was treated as high-value by the dispatcher — that weighting shaped the exception decision. If AERA gives the same automated response to Stein-Allen as to a single-parcel DTC customer, we're eliminating a differentiation that currently exists. I want to know if that data is already in Salesforce, or whether it's dispatcher memory."*

Changes: If flag exists → add strategic account escalation trigger before launch. If no data → data gap requiring remediation before launch.

`[VALIDATED — Gate 2 Artifacts]` APEX_CUSTOMER_MASTER confirms ACCT_MGR field. Hayes & Sons (C-04451) assigned to U-0089 (Sandra W.). Escalation Trigger 9 in D4 is build-ready. This question is now confirmatory, not exploratory.

---

### Live Round: Evasion Detection

| If Sarah says... | Press with... |
|---|---|
| "The chatbot was just bad" | "Was it what it said, or that it was a bot at all?" |
| "The RPA project was the vendor's fault" | "Did Aurum's schema change without notice? That's a design constraint, not a blame question." |
| "Credits are handled by the team" | "Are you aware credits can be applied via manual override without entering the audit log? Is that sanctioned?" |
| "The Driver App team will sort the API out" | "So there's no API today. What's the timeline, and does that gate the ETA agent build?" |
| "We'd have to check the exact numbers" | "Is there someone on your team who runs analytics I could speak with after this session?" |

---

## Deliverable 7 — CLAUDE.md

The full `CLAUDE.md` is at [CLAUDE.md](CLAUDE.md) — the canonical, project-facing file for an AI coding agent. It is the live document an agent reads before writing a single line. The summary below covers the key principles for reviewer navigation; the file contains the complete coding constraints, testing requirements, anti-patterns, and constraint propagation table.

**GPS thresholds (hard limits):**

| Condition | Mode | Action |
|---|---|---|
| GPS ping < 30 min | Autonomous | Respond with best-estimate window |
| GPS ping 30–60 min | Supervised | Widened window + disclosure; flag for review |
| GPS ping > 60 min | Escalate | Never give ETA. Escalate to dispatcher. |
| Driver App unreachable | Escalate | Never respond. Escalate immediately. |

**Exception-first check (mandatory before any response):** Check CRM exception status → check Driver App exception flag → cross-reference APEX_DISPUTES_OPEN. If ANY flag set: do not give ETA.

**Delivery confirmation:** Scan-on-delivery event only. No scan = escalate as potential missing parcel.

**CRM logging:** Non-negotiable. Every interaction logs channel, raw query, mode triggered, response text, GPS age (minutes), exception flag states (CRM/Driver App/Dispute each Y/N/Unknown), and timestamp. Build the logger before the responder.

**Build order:** CRM logger → Order resolver → Autonomy evaluator → Response composer → Escalation router → GPS interpreter (**BLOCKED** until Driver App API confirmed).

**Blocked integrations:** Driver App GPS (API unconfirmed) · Aurum real-time (batch only) · Dispatch Console (Citrix).

**Anti-patterns prohibited:** No GPS position extrapolation from stale pings · No credits without a logged Salesforce audit entry · No Aurum real-time integration · No exception disposition automation · No customer-facing chatbot without explicit Sarah Whitmore approval · No SOP v2.3 as agent knowledge base or ground truth · Do not describe AERA as production-ready until pilot KPI thresholds are confirmed under live conditions.

**Preferred framing:** Say: interruption reduction, context pre-assembly, lookup compression, escalation acceleration. Never say: "automate customer operations," "replace dispatcher decisions," "end-to-end automation."
