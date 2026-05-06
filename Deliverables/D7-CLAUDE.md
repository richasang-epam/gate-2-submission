# Apex ETA Agent — CLAUDE.md

> **D7 — Gate 2 submission, Richa Sang, 2026-05-06**  
> This file is the working project guide for an AI coding agent building the Apex ETA Agent.  
> Read the full Agent Purpose Document before coding: [D4-agent-purpose-document.md](D4-agent-purpose-document.md)  
> Read the system constraints before touching any integration: [D5-system-data-inventory.md](D5-system-data-inventory.md)

---

## What this project is

An agentic worker for Apex Distribution Ltd's Customer Operations function.

**One job only:** resolve "where is my delivery?" inquiries without human intervention for the standard case, and route non-standard cases to the right human with context pre-populated.

**Not a chatbot.** It does not handle exceptions, billing, complaints, or anything other than ETA. Narrow scope is intentional — Apex's prior chatbot failed partly because it tried to do too much.

---

## Architecture (current state — Phase 1 scope)

```
[Inbound message]
      │
      ▼
[Channel parser]      ← SMS webhook / email webhook / (TBD) web portal
      │
      ▼
[Order resolver]      ← Salesforce CRM (REST API) — primary + secondary lookup
      │
      ▼
[GPS interpreter]     ← Driver App backend (REST API — NOT YET CONFIRMED; see below)
      │
      ▼
[Autonomy evaluator]  ← Rules engine: GPS age + exception flags → mode
      │
      ▼
[Response composer] or [Escalation router]
      │
      ▼
[CRM case logger]     ← Salesforce CRM — log every interaction, outcome, mode
```

---

## Build commands

> Update this section once tech stack is confirmed. Stack choice is pending.

```bash
# Placeholder — replace when stack is chosen
npm install        # or pip install -r requirements.txt
npm test           # or pytest
npm run dev        # local dev server
```

---

## Critical constraints — read before writing a single line

### 1. GPS staleness thresholds — hard limits

| Condition | Mode | Action |
|---|---|---|
| GPS ping < 30 min old | Autonomous | Respond with best-estimate window |
| GPS ping 30–60 min old | Supervised | Respond with widened window + disclosure; flag for review |
| GPS ping > 60 min old | Escalate | Never respond with ETA. Escalate to dispatcher. |
| Driver App API unreachable | Escalate | Never respond. Escalate immediately. |

**Do not extrapolate GPS position.** A stale ping is not a prediction; it is the last known fact. Never use it to compute a current position estimate.

### 2. Exception-first check — mandatory before any ETA response

Before composing any response, the agent MUST:
1. Check CRM exception status on the delivery record
2. Check Driver App exception flag (when API is available)
3. Cross-reference APEX_DISPUTES_OPEN daily batch for an open dispute on this order

If ANY flag is set: do not give ETA. Route to exception handler or human agent.

### 3. Delivery confirmation — only from scan event

Never confirm a delivery as completed unless a scan-on-delivery event is explicitly present in Driver App data. If a customer inquires about an order that CRM shows as "delivered" but no scan event exists: escalate immediately as potential missing parcel.

### 4. Scope boundary — do not cross it

| Ask | Correct action |
|---|---|
| "Where is my delivery?" | ✅ Handle |
| "My delivery is damaged" | ❌ Route to exception handler |
| "I want to dispute this charge" | ❌ Route to billing |
| "Can you change my delivery time?" | ❌ Route to dispatch |
| "I want to speak to someone" | ❌ Route to human agent immediately |
| "This is the third time I've asked" | ❌ Escalate (frustration signal) |

### 5. CRM logging — non-negotiable

Every interaction must produce a CRM case entry, including escalations. Fields required:
- Inquiry channel (SMS / email / web)
- Raw query text (for later analysis)
- Mode triggered (Autonomous / Supervised / Escalate-Dispatcher / Escalate-Human)
- Response text sent (or "escalated" with escalation destination)
- GPS ping age at time of query (in minutes)
- Exception flag state (CRM: Y/N; Driver App: Y/N/Unknown; Dispute: Y/N/Unknown)
- Timestamp

Logging failure is not recoverable after the fact. Build the logger before the responder.

### 6. Audit pathway for any billing-adjacent data

This agent does not touch billing. If it ever surfaces invoice or dispute data (e.g., to tell a customer their order is under dispute), it must:
- Disclose that data is from yesterday's batch (T-1)
- Not make any credit, refund, or adjustment decision
- Route all billing questions to the billing team

---

## Systems you may build against (Phase 1)

| System | Status | Notes |
|---|---|---|
| Salesforce CRM | ✅ Build against | REST API confirmed. Credentials in `.env` (see `.env.example`). Confirm rate limits before batch logic. |
| Comms gateway (SMS/email) | ✅ Build against | Confirm provider and credentials. |
| APEX_DISPUTES_OPEN batch | ✅ Build against | Daily CSV ingest pipeline needed. Build schema-change detection first. |

## Systems you must NOT build against yet

| System | Reason | Gate to proceed |
|---|---|---|
| Driver App GPS API | **API not confirmed.** In-house app; no API spec available. | API spec confirmed by Driver App team |
| Aurum Billing (any endpoint) | Batch-only; out of Phase 1 scope | Phase 2 prerequisite: governance fix + batch pipeline |
| Dispatch Console | Citrix — no clean integration | Phase 4 prerequisite: console re-platform |

---

## Open questions — ask before building these components

| Question | Blocks |
|---|---|
| Driver App API spec and GPS telemetry endpoint | All GPS-related code (steps 5–8 in activity catalogue) |
| Salesforce schema: field name for route_code (or equivalent linking delivery to Driver App route) | Step 4 (route retrieval) |
| GPS refresh cadence | Staleness threshold calibration |
| Channel split of 400 ETA inquiries/day | Scope of comms gateway build (1 channel vs 3) |
| Salesforce API rate limits | Batch query design |

---

## What to build first (recommended order)

1. **CRM logger** (Step 12) — build and test in isolation first. Every other step feeds it.
2. **Order resolver** (Steps 2–3) — CRM lookup by order ID + fallback. Mock GPS for now.
3. **Autonomy evaluator** (Step 9) — rules engine. Unit-test against the full scenario matrix in D4 before any integration.
4. **Response composer** (Step 10) — channel-appropriate templates. Do not personalise beyond order/ETA facts.
5. **Escalation router** (Step 11) — must be tested for every trigger before ship. Non-negotiable.
6. **GPS interpreter** (Steps 5–8) — **BLOCKED until Driver App API confirmed.** Do not begin.

---

## Testing requirements

### Unit tests (required before integration)

| Test | Input | Expected output |
|---|---|---|
| GPS fresh | Ping age = 10 min, no flags | Autonomous mode → respond with window |
| GPS borderline supervised | Ping age = 35 min, no flags | Supervised mode → widened window + disclosure |
| GPS stale escalate | Ping age = 65 min | Escalate mode → dispatcher, no ETA given |
| Driver App offline | API error | Escalate mode → dispatcher, no ETA given |
| Exception flag in CRM | exception_status = true, GPS fresh | Escalate mode → exception handler, no ETA given |
| Open dispute cross-reference | APEX_DISPUTES_OPEN contains order | Escalate mode → human agent |
| Order not found (primary) | No CRM match on order ID | Attempt secondary lookup (name + address) |
| Order not found (both lookups) | No CRM match on any identifier | Escalate → human agent |
| Repeat inquiry | Same customer, same order, within 24h | Escalate → human agent (frustration signal) |
| Delivery confirmed by scan | Scan-on-delivery event present | Confirm delivery; log case |
| Delivery "complete" without scan | Delivery status = complete, no scan event | Escalate → potential missing parcel |

### Integration tests

- Salesforce sandbox before production — never test against production CRM
- Replay 50 historical ETA inquiries (if Apex can provide) to validate mode classification accuracy
- Escalation path end-to-end test: verify dispatcher receives full context, not just an alert

### Schema change test (APEX_DISPUTES_OPEN)

- Modify CSV headers in test environment; verify schema-change alert fires and agent does not silently misread data

---

## Response tone constraints

- Never give false precision. "Between 13:00 and 17:00" is better than "around 14:22" when GPS is uncertain.
- Always disclose if an ETA is an estimate vs a confirmed schedule window.
- If escalating: tell the customer what is happening. "I'm passing this to our dispatch team — you'll hear back shortly" is better than silence.
- SMS responses: under 160 characters where possible. Email: concise, no corporate boilerplate.
- Do not apologise for things outside your scope. Do not promise things you cannot deliver.

---

## Known gaps in this document (scope-outs)

| Gap | Plan to resolve |
|---|---|
| Driver App API spec | Discovery question Q1 in D6 — must be answered before GPS build begins |
| Salesforce schema field names | Salesforce schema review session — schedule with Apex IT |
| Channel split (SMS/email/web) | Discovery question Q5 in D6 — affects comms gateway build scope |
| Dispatcher SLA for escalated cases | Operational question for Sarah Whitmore — affects customer-facing message on escalation |
| CSAT measurement method | If no post-interaction survey exists, this must be built or KPI removed |

---

## Preferred operational framing

**The goal is operational compression, not automation.**

- Preferred language: interruption reduction, coordination latency reduction, context pre-assembly, lookup compression, escalation acceleration, workflow compression, visibility enhancement.
- Avoid: "automate customer operations," "replace dispatcher decisions," "fully automate responses," "end-to-end automation."

Agent value at Apex lies in orchestration — tracking, flagging, pre-assembling, routing — not in replacing human judgment or eliminating human oversight.

**Do not describe AERA as production-ready or deployment-ready** until pilot KPI thresholds are confirmed under live conditions. It is a constrained pilot.

---

## Delegation philosophy

**Default assumption: human judgment is required unless explicitly proven otherwise.**

- Agent actions that are observable, reversible, and involve structured lookup with no decision authority: Agent-led with human oversight is acceptable.
- Agent actions involving financial decisions, customer-facing commitments, or exception routing: Human-led with agent support only.
- Agent actions involving dispatch adjustments, exception classification, credit authority, or any real-time irreversible decision: Human-only. Do not build agent decision logic here.

**Before building any agent decision capability, answer all three:**
1. What is the expected override rate?
2. What is the consequence of a wrong decision within the current shift window?
3. Is the system observable enough to catch errors before they cascade?

If any answer is "unknown" — do not build the decision. Build context pre-assembly instead.

---

## Buildability discipline

**Build-ready (suitable for constrained pilot — not production-ready):**
- ETA inquiry compression (Salesforce + Driver App GPS)
- Exception context pre-assembly (Salesforce + Driver App)
- Repeat dispute pattern detection (Salesforce case history only)

**Hypothesis / Pilot required — do not build until pilot validates:**
- Proactive ETA push notifications (baseline measurement + customer acceptance unknown)
- Aurum batch context pre-assembly for billing disputes (8 weeks schema monitoring prerequisite)
- Customer-facing ETA chatbot (explicit Sarah Whitmore approval required; prior chatbot failure creates political risk regardless of technical feasibility)

**Blocked — do not build until the named prerequisite is resolved:**
- Exception classification or disposition recommendation → blocked on SOP Section 4.3 completion and exception protocol definition
- Billing dispute credit recommendation → blocked on credits audit log remediation and credit authority policy definition
- Dispatch adjustment orchestration → blocked on Dispatch Console API confirmation

Treat blocked items as blocked. Do not work around blockers with fragile integrations. If a stakeholder requests a blocked feature, surface the specific blocker before discussing implementation approach.

---

## Evidence discipline

Lived-work evidence from artefacts takes precedence over SOP documentation.

**SOP v2.3 sections invalid for agent design:**
- Any reference to "DispatchHub" — retired October 2024; current tool is Driver App. Do not encode DispatchHub workflows into agent logic.
- Section 4.3 (damaged consignments) — marked "TBD pending review." No decision protocol exists. Do not attempt to infer damage classification rules from surrounding sections.

**Do not use SOP v2.3 as agent knowledge base or training data** without a full revision completed and signed off by Sarah Whitmore.

**Assumption confidence labelling — required on all design decisions:**
- [HIGH] confirmed by artefact, Gate 2 artifact validation, or explicit brief statement
- [MEDIUM] inferred from artefact evidence with reasonable basis
- [LOW] assumption — must be confirmed before committing to build

Known [LOW] assumptions at time of writing: Driver App GPS refresh cadence; % of ETA inquiries requiring dispatch escalation; Salesforce API rate limits; channel split of 400/day inquiries.

---

## Organisational adoption risk

Technical performance alone does not determine deployment success. Monitor these adoption signals with the same rigour as technical KPIs:

- **Bypass behaviour:** Agents handling ETA cases manually that AERA should handle. This is a design signal — diagnose the cause (wrong thresholds, distrust of confidence tiers, perceived overhead), do not penalise it.
- **Shadow workflows:** Agents developing informal workarounds to avoid the escalation queue or systematically override confidence tiers. Treat as evidence of a design gap requiring correction.
- **Dispatcher queue resistance:** If dispatchers hold named-route ownership (Artefact 1 pattern), a generic escalation queue will be ignored regardless of its technical quality. Confirm routing model with dispatchers before build.
- **Surveillance perception:** GPS logging must be scoped to ETA estimation only. Any perception that case-level tracking is individual driver performance monitoring will erode adoption.
- **Scope anxiety:** Dispatchers or agents fearing AERA expansion into exception classification or dispatch decisions. Communicate scope boundaries at launch. Future scope items are blocked on named prerequisites — not a roadmap queue.
- **Metric gaming:** KPI numbers improving while operational quality degrades (rubber-stamped escalations, speeded-up case handling to inflate time-saved). Qualitative 10% case sampling weekly is mandatory alongside quantitative KPI tracking.

Adoption failure is a first-class risk alongside technical failure.

---

## Anti-patterns — explicitly prohibited

- Do not build toward full automation of exception disposition or dispatch decisions.
- Do not design credit recommendation or credit staging without an auditable Salesforce log path. The Aurum credits CSV cannot be the record of truth — audit gaps are confirmed and intermittent.
- Do not integrate with Aurum in real-time — it does not support it.
- Do not present GPS-derived ETA responses as confirmed delivery times. Fresh GPS does not eliminate route volatility uncertainty.
- Do not replicate the manual credit override pattern observed in Artefact 2 (Sandra's £170). The formal APPROVER_ID + AUDIT_REF pathway is the only compliant path.
- Do not use SOP v2.3 as ground truth for agent decision logic.
- Do not build a customer-facing chatbot without explicit Sarah Whitmore approval. Prior chatbot failure creates political risk regardless of technical feasibility.
- Do not extrapolate GPS position from a stale ping. A stale ping is the last known fact, not a prediction.

---

## Constraint propagation summary

| Constraint | Source | Impact on CLM | Impact on DSM | Impact on V×V | Impact on APD |
|---|---|---|---|---|---|
| Aurum: no real-time API, batch T-1/T-2, schema unstable quarterly | Artefact 5 + RPA failure | Hidden work: agents manually parse CSVs; same-day disputes have no data | Billing resolution → Human-only; context pre-assembly → Hypothesis/Pilot | Billing auto-resolution → Blocked; batch pre-assembly → Pilot required | Future scope for real-time features; batch pre-assembly conditional on schema monitoring |
| SOP v2.3 partially obsolete (DispatchHub retired; Section 4.3 blank) | Artefact 4 | Hidden work: dispatchers maintain meta-knowledge SOP is wrong | Exception classification → Human-only (no protocol to encode) | Exception decision automation → Blocked | Exception decision support blocked pending SOP revision |
| Credits audit log: intermittent bypass | Artefact 2 + Gate 2 Artifacts | Hidden compliance risk: credit behaviour is unpredictably unaudited | Billing credit recommendation → Human-only | Billing auto-resolution → Blocked | No credit scope; future credit feature requires guaranteed audit path |
| Dispatch Console: Citrix, API surface unconfirmed | Scenario brief | Hidden work: dispatchers manually bridge between console and Driver App | Dispatch adjustments → Human-only | Dispatch automation → Blocked | All console-dependent features blocked until API confirmed |
| GPS data latency (observed 26+ min in production) + route volatility | Artefact 3 | Hidden work: ETA inquiries require dispatch escalation for fresh data | ETA edge cases → Human-led + Agent Support | ETA compression ceiling capped at ~70%; route volatility is structural floor | Confidence tier system; escalation triggers include GPS age > 60 min |
| Named-dispatcher routing (personal accountability by route) | Artefact 1 | Hidden work: named personal queues; shift-transition orphaning | Exception pre-assembly queue must respect named routing | Queue architecture dependency before exception pre-assembly build | Escalation routing must account for named-dispatcher model; adoption risk if ignored |
