# Deliverable 1 — Cognitive Load Map

> **Apex context (company profile, work stream volumes, system catalogue, artefact findings):**  
> See [_shared-context.md](_shared-context.md) — do not duplicate those facts here.

---

## Scope

Two work streams decomposed in full: **ETA Inquiries** and **Delivery Exceptions**.  
These two were chosen because they sit at opposite ends of the cognitive spectrum — one is structurally close to agentic; the other is irreducibly judgment-driven — and mapping both makes the delegation boundary argument in D2 defensible.

---

## Work Stream 1: ETA Inquiries (400/day, avg 4 min)

### What actually happens (lived, not SOP)

Artefact 3 shows the real workflow: a customer asks where their order is; the agent looks up the CRM to get a route assignment and window; they then make a secondary check with dispatch (manually, not via system) to narrow the estimate when the standard window is too wide. GPS data was stale by 26–36 minutes in the artefact. The agent gave a human best-guess estimate, not a system-computed one.

There is no SOP section for ETA inquiries — it is entirely informal. The 4-minute average likely understates the time in edge cases where the agent must call dispatch.

### Jobs to be Done

| JTBD | Trigger | Done When |
|---|---|---|
| JTBD-ETA-1: Identify the order | Customer submits reference (order ID, phone, name) | Order record confirmed in CRM |
| JTBD-ETA-2: Retrieve current delivery status | Order identified | Route, driver, last GPS position, window known |
| JTBD-ETA-3: Interpret timing | Status retrieved | Confidence-calibrated ETA formed |
| JTBD-ETA-4: Communicate ETA | ETA formed | Customer has responded-to inquiry with useful answer |
| JTBD-ETA-5: Escalate when uncertain | Data insufficient or exception detected | Human dispatcher or exception handler has case |

### Micro-task Decomposition

**JTBD-ETA-1 (Identify):**
- Parse contact channel (SMS / email / phone) for order reference
- Match order reference to CRM record (by order ID, or fallback: customer name + address)
- Confirm customer identity if ambiguous

**JTBD-ETA-2 (Retrieve status):**
- Pull route assignment from CRM delivery record
- Pull driver assignment from route record
- Query Driver App for GPS last ping: timestamp + coordinates
- Check delivery sequence position on current route
- Check for any exception flags on the order (CRM or Driver App)

**JTBD-ETA-3 (Interpret timing):**
- Compare GPS last ping timestamp to current time → staleness delta
- Estimate remaining stops and average time per stop on this route
- Cross-check with scheduled delivery window
- Apply staleness uncertainty: widen window if GPS > 30 min stale
- If exception flag present: do not give ETA — route to exception handler

**JTBD-ETA-4 (Communicate):**
- Compose channel-appropriate response (SMS: brief; email: slightly fuller)
- Disclose if estimate vs confirmed window
- Invite customer to follow up if delivery misses estimate

**JTBD-ETA-5 (Escalate):**
- If GPS stale beyond threshold → pass to dispatcher with pre-populated context
- If order in exception → route to exception handler with order details
- If customer shows frustration signals (repeat inquiry, explicit complaint) → human agent

### Cognitive Dimensions

| Dimension | Rating | Evidence |
|---|---|---|
| **Working memory load** | Low–Medium | Standard case: 3–4 data points (order, route, GPS, window). Stale GPS case: must hold uncertainty and form a hedged estimate. |
| **Pattern recognition** | Low–Medium | "Route 028, last ping Watford 10:48, 11:16 now" → dispatcher knew to estimate ~14:00. Requires knowing route geography and typical pace — not trivial. |
| **Judgment calls** | Low (standard) / Medium (edge) | Is GPS staleness acceptable? Is the exception flag accurate? Is the customer going to escalate? |
| **Emotional labour** | Low (standard) / Medium (frustrated customer) | Most ETA calls are neutral; repeat inquirers are often mildly frustrated. No high-stakes emotional work. |
| **Context dependency** | Low | Each inquiry is largely independent; account history rarely relevant for ETA. |
| **Time pressure** | Low–Medium | Customer wants a quick answer but this is not real-time critical like dispatch. |

### Zone Map

```
ZONE A — Fully agentic (~65–70% of cases)
  Conditions: order found, GPS ping <30 min old, no exception flag
  Cognitive work: structured lookup + response
  Agent action: respond with ETA window, log CRM case

ZONE B — Agent-led with human oversight (~20% of cases)
  Conditions: GPS ping 30–60 min stale, or minor ambiguity in order match
  Cognitive work: agent forms widened estimate; flags for human review
  Agent action: draft response with uncertainty disclosure; passive supervisor can override

ZONE C — Human-led with agent support (~10% of cases)
  Conditions: GPS >60 min stale, driver app offline, order in exception state,
              customer repeat inquiry (frustration signal)
  Cognitive work: dispatcher judgment needed; agent prepares context
  Agent action: escalate with order + route + GPS context pre-populated; human responds

ZONE D — Human-only (<5% of cases)
  Conditions: Active dispute on order, high-value account needing relationship handling,
              customer threatening legal/complaint escalation
  Cognitive work: relationship management, not ETA lookup
  Agent action: route to named account manager; do not intervene
```

### Breakpoints

| Breakpoint | Trigger | Consequence if Missed |
|---|---|---|
| GPS staleness threshold (30 min / 60 min) | Age of last GPS ping | Agent gives false-precision ETA for driver who may have diverted |
| Exception flag on order | CRM or Driver App exception status | Agent tells customer delivery is coming; delivery won't happen |
| Repeat inquiry from same customer within 24h | CRM case history | Agent gives same unhelpful answer twice; customer escalates publicly |
| Order not found after primary lookup | No CRM match on first attempt | Agent must attempt secondary lookup (name/address); fail → escalate |

---

## Work Stream 2: Delivery Exceptions (180/day, avg 12 min)

### What actually happens (lived, not SOP)

Artefact 1 shows the reality: a driver calls in a judgement-heavy situation. The pallet "looks fine" to the driver but the warehouse operative won't accept it. The site manager is unavailable. The driver has 6 more drops. No one has called back yet (Sandra was busy). The dispatcher must make a call — return-to-depot, hold, attempt delivery at the operative's risk — based on a verbal description, the account's value, the driver's remaining schedule, and an incomplete SOP (Section 4.3 is literally blank).

SOP v2.3 is outdated: it references DispatchHub (retired Oct 2024, replaced by the current Driver App). Section 4.3 (damaged consignments) is incomplete. The team is operating on institutional knowledge and individual dispatcher judgment.

**Observed subtypes from artefacts:**
- Refused delivery (damage concern) — Artefact 1
- Damaged consignment with billing consequence — Artefact 2 (spills into billing dispute)
- Delivery to unattended address — SOP 4.4 reference (content not shown)
- High-value consignment escalation (>£500 → Duty Manager)

### Jobs to be Done

| JTBD | Trigger | Done When |
|---|---|---|
| JTBD-EX-1: Triage the exception | Driver/system alert or inbound call | Exception type, urgency, and account profile known |
| JTBD-EX-2: Retrieve delivery and account context | Exception triaged | Customer history, contract type, consignment value, driver status all known |
| JTBD-EX-3: Decide disposition | Context assembled | One of: return-to-depot / re-attempt / leave with acknowledgement / hold / escalate to manager |
| JTBD-EX-4: Instruct the driver | Decision made | Driver has a clear, unambiguous action and timeline |
| JTBD-EX-5: Notify customer (where appropriate) | Decision made | Customer informed of outcome (not always done — depends on account type and severity) |
| JTBD-EX-6: Log and close the case | Action taken | CRM case complete; claims/billing flags raised if needed |
| JTBD-EX-7: Flag downstream implications | Damage/billing trigger | Billing team or claims handler notified if commercial consequence expected |

### Micro-task Decomposition

**JTBD-EX-1 (Triage):**
- Identify exception type (refusal, damage, unattended, missed window, accident)
- Assess urgency: is driver parked waiting? Time remaining on shift? Route impact?
- Flag high-value threshold (>£500 → Duty Manager escalation required per SOP 4.2)

**JTBD-EX-2 (Context retrieval):**
- Pull customer account from CRM (contract type, account tier, credit limit, history)
- Check for prior exceptions on this account or consignment
- Pull consignment details (declared value, contents type, fragility)
- Check driver's remaining route (number of stops, total time)
- Check current Duty Manager availability if high-value flag

**JTBD-EX-3 (Decide disposition):**
- Interpret driver's description of damage or refusal (with no visual — purely verbal/text)
- Apply judgment: is this a reasonable refusal or a warehouse operative being overcautious?
- Weigh: account relationship value vs operational cost of return vs driver schedule impact
- Consult SOP — but Section 4.3 is incomplete; dispatcher falls back on experience
- For high-value: consult Duty Manager (SOP 4.2 requirement)

**JTBD-EX-4 (Instruct driver):**
- Call or message driver with explicit decision and reasoning
- Confirm driver understanding and capability to execute (e.g., can they physically hold the item?)

**JTBD-EX-5 (Customer notification):**
- Decide whether customer needs to be informed immediately or post-resolution
- For B2B accounts: proactive notification expected; for DTC: variable
- Draft communication or instruct agent to call

**JTBD-EX-6 + EX-7 (Log and flag):**
- Close CRM case with disposition, rationale, and timestamp
- If damage confirmed: flag for insurance/claims review (protocol currently undocumented — SOP 4.3 blank)
- If billing implication: notify billing team to expect dispute (Artefact 2 shows this cross-reference is missed in practice)

### Cognitive Dimensions

| Dimension | Rating | Evidence |
|---|---|---|
| **Working memory load** | High | Dispatcher must simultaneously hold: driver's situation, 6 remaining drops, account value, damage description, Duty Manager availability, incomplete SOP guidance, customer relationship. Artefact 1 illustrates this concretely. |
| **Pattern recognition** | High | "New warehouse guy, site manager not here, pallet corner" — requires experience to assess whether this is genuine damage or operational friction. Not systematisable without visual confirmation. |
| **Judgment calls** | Very high | The core of exception handling IS dispatcher judgment. No rule covers all cases; SOP is incomplete; edge cases dominate. |
| **Emotional labour** | Medium–High | Driver is stressed (time pressure, uncertain). Dispatcher must manage driver anxiety while making a sound operational decision under pressure. |
| **Context dependency** | Very high | The right answer depends on account history, consignment value, driver schedule, duty manager availability, and insurance protocol — all of which change case by case. |
| **Time pressure** | High | Driver is parked. Route schedule is running. Each minute of decision delay compounds cost. |

### Zone Map

```
ZONE A — Fully agentic (near-zero)
  Conditions: None identified. Exception handling requires interpreter judgment on ambiguous
              physical/relational situations. SOP is incomplete. No safe fully-agentic path.

ZONE B — Agent-led with human oversight (~20–25% of the cognitive work)
  Conditions: Triage and context assembly steps (JTBD-EX-1 and EX-2)
  Agent action: identify exception type, pull account/consignment/route context,
                flag high-value threshold, surface prior exceptions on account,
                pre-populate dispatcher screen
  Human role: review context and make the disposition decision

ZONE C — Human-led with agent support (~65–70% of the cognitive work)
  Conditions: All disposition and instruction decisions (JTBD-EX-3, EX-4, EX-5)
  Agent action: surface relevant SOP sections (with staleness warning), show account tier,
                suggest standard templates for driver instructions
  Human role: all decisions

ZONE D — Human-only (~10%)
  Conditions: High-value (>£500), confirmed damage, insurance protocol trigger,
              Duty Manager escalation, customer account at risk
  Agent action: route to appropriate person; no intervention
  Human role: Duty Manager / senior agent owns end-to-end
```

### Breakpoints

| Breakpoint | Trigger | Consequence if Missed |
|---|---|---|
| High-value threshold (>£500) | Consignment declared value | Duty Manager escalation not triggered; decision made below authority level |
| SOP incompleteness on damage | Exception type = damage | Agent defaults to incomplete protocol; dispatcher has no documented anchor |
| Insurance protocol trigger | Damage confirmed | Claims not initiated; evidence window closes; customer complaint follows |
| Billing implication flag | Damage + existing invoice | Billing team not notified; customer raises dispute later (as in Artefact 2) |
| Driver schedule clock | Time parked waiting | Route falls behind; downstream deliveries miss windows; SLA breach |

---

## Work Stream 3: Dispatch Adjustments (90/day, avg 18 min)

### What actually happens (lived, not SOP)

No artefact directly documents a dispatch adjustment, but Artefact 1 (Petrov's voicemail) gives a window into the dispatcher's mental state during a high-pressure operational event: they must simultaneously hold the affected driver's situation, the route schedule, the account relationship, and the absence of an available decision-maker. A dispatch adjustment is the proactive version of that same cognitive load — a mid-route change (new pickup added, customer requesting a divert, driver reporting a vehicle issue, weather-driven re-sequence) — executed against a Citrix-deployed console with no clean programmatic interface.

The Dispatch Console's Citrix deployment is not an incidental inconvenience. It means every write action (route change, driver reassignment, exception flag) must be executed manually by a human through a desktop UI. This is a hard architectural constraint that shapes the entire zone map for this work stream.

### Jobs to be Done

| JTBD | Trigger | Done When |
|---|---|---|
| JTBD-DA-1: Receive and classify the request | Inbound call / Driver App alert / customer request | Adjustment type, affected route(s), and urgency established |
| JTBD-DA-2: Assess route impact | Request classified | All directly and indirectly affected routes, stops, and drivers identified |
| JTBD-DA-3: Identify solution options | Impact assessed | 2–3 viable options (reassign, reroute, defer) identified with trade-offs |
| JTBD-DA-4: Execute change in Dispatch Console | Decision made | Route, driver assignment, and stop sequence updated in the system |
| JTBD-DA-5: Notify affected drivers | Change executed | All drivers with route changes have received updated instructions via Driver App |
| JTBD-DA-6: Log outcome and flag SLA risk | Change complete | CRM case logged; any at-risk deliveries flagged for monitoring |

### Micro-task Decomposition

**JTBD-DA-1 (Receive and classify):**
- Identify the trigger (new pickup request, divert request, driver breakdown, road closure, customer re-schedule)
- Determine urgency: is the driver already en route? Has a delivery window been committed?
- Identify all routes potentially affected (the requesting route + any routes that share a depot, driver, or stop sequence)

**JTBD-DA-2 (Assess route impact):**
- Pull real-time driver positions from Driver App for all affected routes
- Check remaining stops and estimated completion times for each driver
- Identify which drivers have buffer capacity vs those running at schedule limit
- Check contractual SLA tier for affected deliveries (high-SLA accounts cannot slip without consequence)

**JTBD-DA-3 (Identify solution options):**
- Option A: add the adjustment to an existing route with buffer
- Option B: reassign to a different driver better positioned geographically
- Option C: defer to the next day (requires customer notification and sign-off)
- Apply dispatcher's knowledge of route geography, driver capabilities, and account priority to rank options

**JTBD-DA-4 (Execute in Dispatch Console):**
- Log in to Dispatch Console (Citrix desktop application)
- Navigate to the affected route; make the change (re-sequence stops, reassign driver)
- Verify the change has been accepted and propagated correctly — no automated confirmation exists

**JTBD-DA-5 (Notify drivers):**
- Send updated route instruction via Driver App to all affected drivers
- Confirm driver has acknowledged and can execute (driver may be mid-delivery and unable to respond immediately)

**JTBD-DA-6 (Log and flag):**
- Close CRM case with adjustment type, rationale, and outcome
- Flag any deliveries now at SLA risk for proactive customer notification

### Cognitive Dimensions

| Dimension | Rating | Evidence |
|---|---|---|
| **Working memory load** | Very High | Dispatcher must simultaneously hold 2–4 affected routes, each with multiple remaining stops, driver positions, and SLA obligations. A change to one route recalculates risk across all others. |
| **Pattern recognition** | High | Experienced dispatchers know which routes have buffer time vs tight sequences, which drivers run fast vs slow, and which geographic zones have traffic risk at which times. None of this is codified. |
| **Judgment calls** | High | When two options both create SLA risk, a call must be made: which account is higher priority? Which driver can absorb the extra stop? No rule resolves this — it requires operational judgment. |
| **Emotional labour** | Medium | Driver is parked waiting; customer may have been given a committed window; pressure for speed creates errors if decision is rushed. |
| **Context dependency** | Very High | The right answer depends on real-time driver positions, current route states, remaining stops across multiple vehicles, traffic, account SLA tiers, and driver shift hours — all of which change by the minute. |
| **Time pressure** | Very High | Mid-route decisions are seconds-to-minutes. Each minute of delay propagates downstream: drivers wait, routes fall behind, SLA windows close. |

### Zone Map

```
ZONE A — Fully agentic (near-zero)
  Conditions: The Citrix integration barrier makes fully autonomous execution technically
              impossible without RPA-class automation (which is brittle and replicates the
              failure mode of Apex's prior project). Even if the technical barrier were
              removed, the high error consequence and multi-vehicle cascade risk make
              unsupervised autonomous execution inappropriate.

ZONE B — Agent-led with human oversight (~10–15% of the cognitive work)
  Conditions: Context assembly before the dispatcher acts
  Agent action: Pull real-time driver positions, remaining stops, SLA tier for all
                affected routes; surface buffer capacity by driver; flag high-SLA
                accounts at risk — all displayed on dispatcher screen before they act
  Human role: Reviews context; makes the adjustment decision; executes in Dispatch Console

ZONE C — Human-led with agent support (~75–80% of the cognitive work)
  Conditions: All decision and execution steps (JTBD-DA-3, DA-4, DA-5)
  Agent action: Surface route maps, stop counts, driver acknowledgement status
                alongside the console; provide templates for driver notification messages
  Human role: All decisions; all Dispatch Console interactions

ZONE D — Human-only (~10%)
  Conditions: High-consequence adjustments — multi-vehicle re-routing, SLA breach
              inevitable, high-value account at risk, driver welfare concern
  Agent action: Route to senior dispatcher or operations manager
  Human role: Senior dispatcher owns end-to-end
```

### Breakpoints

| Breakpoint | Trigger | Consequence if Missed |
|---|---|---|
| Multi-vehicle cascade check | Any route adjustment | Changing one route without checking all affected routes → downstream SLA breaches across multiple drivers |
| SLA tier awareness | Any stop re-sequence | A low-value stop swapped ahead of a high-SLA account → contract breach and penalty exposure |
| Driver shift hours / capacity | Any additional stop assignment | Assigning extra stops to a driver already at safe hours limit → compliance risk; driver may refuse |
| Citrix write dependency | Any automation attempt on Dispatch Console | Scripted UI automation fails on any UI update — same failure mode as prior RPA project |

---

## Work Stream 4: Billing Disputes (60/day, avg 28 min)

### What actually happens (lived, not SOP)

Artefact 2 is the direct evidence: Hayes & Sons disputes INV-2026-04318 over a fuel surcharge. Sandra looks up the invoice in Aurum (the 2008 on-prem Oracle system), cross-references the fuel surcharge calculation file, assesses the claim, and applies a £170 goodwill credit via a manual workaround — bypassing the formal APPROVER_ID + AUDIT_REF pathway entirely. The batch data (APEX_DISPUTES_OPEN, D-2026-00342) shows the dispute still as PENDING_CLAIM — the manual credit did not close the record in the system.

Artefact 5 cross-reference: Hayes & Sons (C-04451) has 3 FUEL_SURCH_DAMAGE disputes open in 2026 (D-2026-00338, 00341, 00342). These are not isolated events — this is a systemic pattern in the account that is not being managed as one.

The 28-minute handling time almost certainly includes: Aurum loading time (legacy on-prem Oracle, known to be slow), navigation through Aurum screens, time cross-referencing CSV files manually, and drafting a customer response. Active decision-making — "what is the right resolution here?" — is probably 5–8 minutes. The rest is system friction and waiting. This is critical context for the automation opportunity: the agent cannot speed up Aurum, but it can eliminate almost all of the retrieval and cross-referencing time.

### Jobs to be Done

| JTBD | Trigger | Done When |
|---|---|---|
| JTBD-BD-1: Parse and classify the dispute | Inbound dispute (email, CRM case, call) | Dispute type, invoice reference, customer, and amount identified |
| JTBD-BD-2: Retrieve invoice and surcharge data | Dispute classified | Relevant invoice, surcharge breakdown, credit history, and prior disputes assembled |
| JTBD-BD-3: Validate the claim | Data retrieved | Claim compared against actual records; discrepancy or validity confirmed |
| JTBD-BD-4: Determine resolution | Claim validated | One of: credit / rejection with evidence / escalation for approval / request for clarification |
| JTBD-BD-5: Execute or stage resolution | Decision made | Credit staged for approval via formal pathway, OR rejection drafted, OR escalation raised |
| JTBD-BD-6: Communicate outcome | Resolution staged | Customer has a factually accurate response with timeline |
| JTBD-BD-7: Log and flag | Outcome communicated | CRM case closed; Aurum dispute status updated (or flagged for update); repeat-pattern flag raised if applicable |

### Micro-task Decomposition

**JTBD-BD-1 (Parse and classify):**
- Identify dispute type (FUEL_SURCH_DAMAGE, DIM_WEIGHT_DISPUTE, REDELIVERY_FEE, DAMAGE_CLAIM — from APEX_DISPUTES_OPEN taxonomy)
- Extract invoice reference number and cross-reference to customer record in CRM
- Identify the disputed amount and the period it relates to

**JTBD-BD-2 (Retrieve data):**
- Pull the T-1 Aurum batch: relevant invoice record (APEX_BILL_DAILY), fuel surcharge breakdown (APEX_FUEL_SURCH), credit history (APEX_CREDITS), reconciliation record (APEX_RECON), and prior disputes (APEX_DISPUTES_OPEN) for this customer
- Check customer master for account tier, credit limit, and account manager (APEX_CUSTOMER_MASTER)
- Note T-1 lag: all data is from yesterday's batch — if the customer is querying today's invoice or today's delivery, the data may not yet be present

**JTBD-BD-3 (Validate the claim):**
- Cross-reference the disputed surcharge amount against APEX_FUEL_SURCH CALC_TIMESTAMP and FUEL_PCT for the relevant route
- Verify the surcharge calculation is arithmetically correct against the contracted RATE_CARD
- Check APEX_CREDITS for any prior goodwill credit on this account — was this dispute partially resolved before?
- Check APEX_RECON for any outstanding variance on this invoice

**JTBD-BD-4 (Determine resolution):**
- If the surcharge is arithmetically wrong: straightforward credit — but requires APPROVER_ID and AUDIT_REF, and 48h turnaround for invoice-level modification
- If the surcharge is correct but disputed on grounds of service failure: goodwill credit decision — requires authority threshold check (who can approve what amount?)
- If pattern is detected (same customer, same dispute type, 3x in 2026): escalate to account manager for relationship conversation, not just dispute resolution
- If data is insufficient (T-1 lag means today's invoice not yet in batch): inform customer of data lag; commit to response by next business day

**JTBD-BD-5 (Execute or stage):**
- If credit approved within agent's authority: stage via formal APPROVER_ID + AUDIT_REF pathway (not the manual override Sandra used)
- If credit exceeds authority: draft for manager approval with all supporting data assembled
- If rejection: draft factually accurate response with surcharge calculation evidence

**JTBD-BD-6 and BD-7 (Communicate and log):**
- Draft customer response with specific invoice figures, not generic language
- If credit: communicate 48h turnaround for invoice modification (not the credit itself, which can be applied faster as a goodwill payment)
- Close CRM case; flag Aurum dispute for status update by billing team (agent cannot update Aurum directly)
- If 3+ disputes on same account in rolling period: flag for account manager review

### Cognitive Dimensions

| Dimension | Rating | Evidence |
|---|---|---|
| **Working memory load** | Medium | Invoice data, surcharge calculation, credit history, account tier, and authority limits — manageable but must be held together. Less than Exception handling because the data is mostly structured and retrievable. |
| **Pattern recognition** | Medium | Dispute types are categorisable; experienced agents recognise FUEL_SURCH_DAMAGE patterns quickly. Less pattern-recognition-intensive than exception handling because there is no ambiguous physical reality to interpret — just numbers. |
| **Judgment calls** | Medium | Key judgment: what is the right resolution for this account relationship? Is a £170 credit appropriate for Hayes & Sons given their dispute history? Is this a goodwill decision or a calculation-error correction? These are different. |
| **Emotional labour** | Low–Medium | Billing disputes are rarely real-time urgent. Customers are frustrated but not in physical distress. The agent has time to think. |
| **Context dependency** | High | The right resolution depends on account tier, prior dispute history, credit limit headroom, the current dispute pattern across the account, and the credit authority structure — all of which must be assembled before a sound decision can be made. |
| **Time pressure** | Low | Disputes are resolved over days. Customer expectation is a response within 24–48 hours, not minutes. The 28-minute handling time is not driven by urgency — it is driven by system friction (Aurum load times, CSV navigation). |

### Zone Map

```
ZONE A — Fully agentic (0%)
  Conditions: Not achievable in Phase 1 or Phase 2 as designed.
  Reason: Aurum's batch-only architecture means the agent cannot retrieve real-time invoice
          data, apply credits synchronously, or close dispute records. Any "fully agentic"
          billing resolution requires a live Aurum API — which does not exist and is not planned.

ZONE B — Agent-led with human oversight (~30–35% of the cognitive work)
  Conditions: Triage, data retrieval, claim validation, and response drafting
  Agent action: classify dispute type; pull the full Aurum data package from T-1 batch
                (invoice, surcharge, credits, prior disputes, customer master);
                validate arithmetic of the surcharge calculation against contracted rate card;
                cross-reference APEX_DISPUTES_OPEN for pattern detection;
                draft a factually accurate response for human review;
                flag if this is the Nth dispute of the same type for the same customer
  Human role: Reviews agent's data assembly and draft; makes the resolution decision

ZONE C — Human-led with agent support (~55–60% of the cognitive work)
  Conditions: Resolution decision and credit approval (JTBD-BD-4, BD-5)
  Agent action: surface credit authority thresholds; show prior approval history from
                APEX_CREDITS; provide credit staging template with APPROVER_ID + AUDIT_REF
                fields pre-populated; block any attempt to apply credit via manual override
  Human role: Decides resolution; approves or rejects credit; signs off on customer
              communication before it is sent

ZONE D — Human-only (~10%)
  Conditions: High-value disputes; potential legal or contract implications; account at
              risk of churn; escalation to senior manager required
  Agent action: Route to account manager or finance team lead
  Human role: Senior agent / account manager owns the resolution end-to-end
```

### Breakpoints

| Breakpoint | Trigger | Consequence if Missed |
|---|---|---|
| Credit authority threshold | Any credit proposal | Credit applied without appropriate APPROVER_ID → audit trail failure (already happening — Artefact 2) |
| T-1 data lag disclosure | Any invoice reference from current day | Agent responds based on yesterday's batch when today's data is not yet available → factual error in response |
| Dispute record closure | Any credit applied | Credit is applied but dispute record not updated in Aurum → customer's dispute appears unresolved in the system; customer re-raises (Artefact 2 pattern) |
| Repeat pattern detection | 2+ disputes of same type on same account | Treating each Hayes & Sons dispute as isolated → systemic account issue is managed as individual incidents; root cause never addressed |

---

## Cross-stream Observation

All four work streams share one structural feature: CRM context assembly is a prerequisite before action. The depth varies dramatically:
- **ETA:** 3–4 data points (order → route → GPS → window). Simple lookup.
- **Billing Disputes:** 6–7 data items from Aurum batch + CRM (invoice, surcharge, credits, disputes, customer master, account tier). Structured retrieval, medium depth.
- **Dispatch Adjustments:** Real-time multi-route state across 2–4 drivers + SLA tier + shift hours. High depth, real-time dependency.
- **Delivery Exceptions:** 6–8 data points including unstructured verbal input + SOP + Duty Manager availability. Complex, partially unstructured.

This means a **shared context-assembly layer** is viable in principle — same architecture, profoundly different depth and data sources per work stream. The ETA agent is the right place to build and prove this pattern before extending it to the more complex work streams.
