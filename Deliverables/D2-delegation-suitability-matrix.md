# Deliverable 2 — Delegation Suitability Matrix

> **Apex context:** See [_shared-context.md](_shared-context.md)  
> **Cognitive Load Map (ETA and Exception detail):** See [D1-cognitive-load-map.md](D1-cognitive-load-map.md)

---

## Scoring Method

Each work stream is scored across six delegation dimensions on a 1–5 scale.  
Dimensions marked **(INV)** are inverse-scored: higher score = harder to automate.

| Dimension | What it measures | 1 | 5 |
|---|---|---|---|
| **Repeatability** | How structured and rule-governed is the task? | Highly variable, case-by-case | Fully rule-based, predictable |
| **Data availability** | Is the required data accessible in real-time via API? | Not available / batch-only | Fully available, real-time API |
| **Error consequence (INV)** | How bad is a wrong automated decision? | Trivial, easily corrected | Catastrophic, irreversible |
| **Time pressure** | How quickly must the task complete? | Days / no urgency | Seconds / real-time critical |
| **Judgment required (INV)** | How much non-rule-based discretion is needed? | Fully rule-based | Irreducible human judgment |
| **Regulatory / compliance (INV)** | How much audit, legal, or financial risk? | None | High compliance obligation |

**Automation readiness score** = average of raw scores, with INV dimensions treated as (6 - score) before averaging. A higher final score = more delegation-ready.

---

## Work Stream Scores

### 1. ETA Inquiries (400/day, 4 min avg)

| Dimension | Raw Score | Adjusted | Notes |
|---|---|---|---|
| Repeatability | 5 | 5 | Highly structured: order ID → route → GPS → window → respond |
| Data availability | 4 | 4 | CRM REST API confirmed; Driver App API assumed (not confirmed) |
| Error consequence **(INV)** | 2 | 4 | ETA slightly off = minor customer frustration; not financially consequential |
| Time pressure | 3 | 3 | Customer wants quick response; not seconds-critical like dispatch |
| Judgment required **(INV)** | 2 | 4 | Standard case is lookup-only; edge cases (stale GPS) require threshold rule |
| Regulatory **(INV)** | 1 | 5 | No compliance obligation; no financial or legal risk |
| **Automation readiness score** | | **4.2 / 5** | |

**Archetype: Agent-led with oversight**

*Rationale:* The standard case is fully automatable — it is a structured lookup with a rule-based response. This earns a high score. It does not earn "fully agentic" because: (a) Driver App API availability is assumed, not confirmed; (b) GPS staleness creates an unavoidable edge condition that requires escalation logic with a human fallback; (c) Artefact 3 demonstrates that even agents who know the route still need dispatcher judgment to narrow a 4-hour window. The escalation path must work before the fully-agentic case can be declared safe.

*"Fully agentic" would require:* Driver App API confirmed + GPS refresh cadence known + exception flag integration tested + escalation path validated. This is Phase 2, not Phase 1.

---

### 2. Delivery Exceptions (180/day, 12 min avg)

| Dimension | Raw Score | Adjusted | Notes |
|---|---|---|---|
| Repeatability | 2 | 2 | Highly variable: damage, refusal, unattended, high-value, SOP incomplete |
| Data availability | 3 | 3 | CRM available; Driver App partial; SOP is outdated; damage protocol absent |
| Error consequence **(INV)** | 4 | 2 | Wrong call = driver stranded, customer lost, insurance gap, SLA breach |
| Time pressure | 4 | 4 | Driver is parked waiting; each minute costs route schedule |
| Judgment required **(INV)** | 5 | 1 | Dispatcher discretion IS the core of exception handling; not substitutable |
| Regulatory **(INV)** | 3 | 3 | Insurance protocol involved; damage claims have legal dimension; SOP gap |
| **Automation readiness score** | | **2.5 / 5** | |

**Archetype: Human-led with agent support**

*Rationale:* Dispatcher judgment is the irreducible core of exception handling. Artefact 1 makes this concrete: the decision (return-to-depot vs hold vs attempt) cannot be made from data alone — it requires interpreting a verbal damage description, knowing the account relationship, assessing the driver's remaining schedule, and applying an insurance protocol that is literally blank in the SOP. The agent's role is context assembly (triage, account pull, history, high-value flag) — not decision-making. Assigning this as "fully agentic" or even "agent-led" would expose Apex to operational failure on the cases that matter most.

*Agent-available scope:* JTBD-EX-1 (triage/classification) and JTBD-EX-2 (context retrieval) are agentic. Disposition and instruction are not.

---

### 3. Dispatch Adjustments (90/day, 18 min avg)

| Dimension | Raw Score | Adjusted | Notes |
|---|---|---|---|
| Repeatability | 3 | 3 | Structured parameters (add pickup, divert, swap driver) but context-driven logic |
| Data availability | 2 | 2 | Dispatch Console is Citrix-deployed — no clean API; read/write both blocked |
| Error consequence **(INV)** | 5 | 1 | Wrong adjustment = multi-vehicle ripple effect, SLA breach, driver conflict |
| Time pressure | 5 | 5 | Mid-route changes are time-critical; delay compounds across all affected routes |
| Judgment required **(INV)** | 4 | 2 | Requires route knowledge, driver capacity, traffic awareness — significant expertise |
| Regulatory **(INV)** | 2 | 4 | Contractual SLA obligations; no direct regulatory risk |
| **Automation readiness score** | | **2.8 / 5** | |

**Archetype: Human-led with agent support**

*Rationale:* Despite a moderate automation readiness score, dispatch adjustments face a hard technical constraint: the Dispatch Console is Citrix-deployed with a "limited API surface." This means any agentic write access to routes or driver assignments requires either a Citrix automation layer (RPA-class, brittle) or a significant Dispatch Console re-platforming effort. Neither is appropriate as a first-phase agentic project. The high consequence of error (a wrong driver swap cascades across multiple routes) and the time pressure (seconds-to-minutes window to act) make this a case where human expertise with rapid agent context-surfacing is the right model. Note: this work stream becomes more agentic if Apex ever re-platforms the Dispatch Console with a proper API — that is a prerequisite, not an agent design problem.

*Agent-available scope:* Surfacing context (driver locations, route options, capacity) to support a human dispatcher's real-time decision.

---

### 4. Billing Disputes (60/day, 28 min avg)

| Dimension | Raw Score | Adjusted | Notes |
|---|---|---|---|
| Repeatability | 3 | 3 | Dispute types are categorisable (fuel surcharge, dim weight, redelivery, damage); resolution is not |
| Data availability | 2 | 2 | Aurum batch-only; T-1 lag; no real-time; 48h modification turnaround |
| Error consequence **(INV)** | 3 | 3 | Incorrect credit = P&L impact; missed credit = customer attrition risk |
| Time pressure | 1 | 1 | Disputes resolved over days; no seconds-urgency |
| Judgment required **(INV)** | 3 | 3 | Policy interpretation, account relationship context, credit authority — moderate |
| Regulatory **(INV)** | 4 | 2 | Audit trail required; credits audit gap observed (Sandra bypass); financial controls at risk |
| **Automation readiness score** | | **2.3 / 5** | |

**Archetype: Human-led with agent support**

*Rationale:* Billing disputes score low primarily because Aurum's batch-only architecture creates a hard ceiling on what an agent can do in real-time. An agent cannot retrieve an invoice, adjust a line item, or apply a credit synchronously — it can only read yesterday's data and queue actions that take 48 hours to execute. The audit trail gap (Artefact 2: Sandra's £170 manual override with no credit log entry) is an additional governance risk: an agent operating in this environment without a properly enforced audit pathway would compound an existing control failure. The agent's productive role is: parse the dispute type, surface the correct invoice and surcharge data from the T-1 batch, draft a response, and stage a credit for human approval — all within the formal APPROVER_ID + AUDIT_REF pathway.

*"Fully agentic" is impossible here without:* a real-time Aurum API (not planned), a tested audit trail enforcement mechanism, and resolution of the manual override pattern currently bypassing formal controls.

---

## Summary Table

| Work Stream | Volume/Day | Readiness Score | Archetype | Primary Constraint |
|---|---|---|---|---|
| ETA Inquiries | 400 | **4.2 / 5** | **Agent-led with oversight** | Driver App API confirmation; GPS staleness logic |
| Delivery Exceptions | 180 | 2.5 / 5 | Human-led with agent support | Dispatcher judgment irreducible; SOP incomplete |
| Dispatch Adjustments | 90 | 2.8 / 5 | Human-led with agent support | Citrix integration barrier; high error consequence |
| Billing Disputes | 60 | 2.3 / 5 | Human-led with agent support | Aurum batch-only hard ceiling; audit trail gap |

---

## Anti-pattern note

The two prior failed automation projects at Apex (chatbot, RPA billing) were both over-scoped relative to the actual system and human-judgment constraints. This matrix is intentionally conservative on archetypes precisely because the evidence from the artefacts shows that the "easy" surface of each work stream conceals real judgment and system complexity. Over-claiming automation readiness is the failure mode the prior projects demonstrated. Coaching this to "fully agentic" across the board would be a repeat of that pattern.
