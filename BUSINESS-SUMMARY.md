# Gate 2 — Business Summary

**What this submission is:** An assessment of how to introduce AI into Apex Distribution Ltd's Customer Operations function — done honestly, with clear boundaries about what AI can and can't do given Apex's current systems and ways of working.

**Audience:** This document is for a business reader who wants to understand the 7 technical deliverables without reading them in full.

---

## What Apex is dealing with

Apex's Customer Operations team of 35 people handles 730 customer interactions a day across four types of work:

- **"Where is my delivery?"** — 400 calls/messages a day, 4 minutes each
- **Driver problems** (damage, refusals, missed windows) — 180 a day, 12 minutes each
- **Route changes mid-delivery** — 90 a day, 18 minutes each
- **Billing disputes** — 60 a day, 28 minutes each

The COO, Sarah Whitmore, wants to use AI on this. She's already tried twice — a customer chatbot that customers hated, and an automated billing tool that broke every time the billing system changed. She's sceptical, and rightly so.

---

## What the 7 deliverables do

### Deliverable 1 — Cognitive Load Map
**What it is:** A detailed breakdown of how all four types of work *actually* happen — not what the rulebook says, but what people are really doing and thinking in each work stream.

**Key findings:**

*"Where is my delivery?"* is mostly a data lookup: find the order, check the GPS, tell the customer. About 65–70% of these cases are a structured, deterministic task that AI can handle without human involvement.

*"Driver is stuck at a refused delivery"* is the opposite: the dispatcher must simultaneously hold the account relationship, the driver's remaining schedule, an incomplete insurance rulebook, and a description of damage they cannot see — all under time pressure, with a driver parked waiting. No rule covers every case. This cannot be automated.

*Route adjustments mid-delivery* are similarly complex: changing one driver's route ripples across every other driver on connected routes. The system for making these changes (Dispatch Console, running on Citrix) cannot even be accessed by AI without a major infrastructure overhaul.

*Billing disputes* sit in the middle: the work is mostly structured (find the invoice, check the surcharge calculation, determine if a credit is appropriate) — but the system holding all this data (Aurum, built in 2008) only exports data once a day and cannot make real-time changes. AI can do the data retrieval and draft a response, but cannot execute the resolution.

**Why it matters:** If we treat all four work streams as equally automatable, we'll repeat Apex's prior mistakes. The map shows, precisely and by work type, which parts are structured enough for AI and which parts depend on human experience and judgment. That distinction drives every recommendation that follows.

---

### Deliverable 2 — Delegation Suitability Matrix
**What it is:** A scored assessment of which work streams are suitable for AI to lead, which ones AI can only assist with, and which must stay human-led.

**The verdict:**

| Work | AI's role | Why |
|---|---|---|
| "Where is my delivery?" | AI leads, human on standby | High volume, structured lookup, low risk if slightly wrong |
| Driver exceptions | Human leads, AI assists | Dispatcher judgment is irreplaceable; the rulebook is incomplete |
| Route adjustments | Human leads, AI assists | The routing software can't be connected to AI without a major upgrade; errors cascade across multiple drivers |
| Billing disputes | Human leads, AI assists | The billing system only updates once a day; AI can't respond in real time; audit controls must be fixed first |

**Why it matters:** The biggest failure pattern in AI projects is assuming everything can be automated. This deliverable deliberately argues against that. Two of the four work streams score below 3 out of 5 for automation readiness. The submission names this openly.

---

### Deliverable 3 — Volume × Value Analysis
**What it is:** A comparison of the four work streams to identify where AI investment delivers the highest return for the lowest risk.

**The recommendation:** Start with "Where is my delivery?" — the ETA inquiry stream. Here's why:
- It's 55% of all cases (400/day)
- ~70% of those cases are a simple data lookup: find the order, check the GPS, reply
- The data needed (order records + GPS position) is accessible via existing systems
- If the AI gets it slightly wrong, the customer just gets a wider time window — not a disaster
- It's buildable now, without touching the problematic billing system or the Citrix routing software

**Estimated impact:** If AI handles 70% of ETA inquiries, that's roughly 1,120 minutes per day (about 18.7 person-hours) freed up — equivalent to about 2.5 full-time staff's worth of capacity, which can be redeployed to higher-judgment work.

---

### Deliverable 4 — Agent Purpose Document
**What it is:** The detailed specification for the AI system that would handle ETA inquiries — precise enough that a developer could start building it.

**How it works:**
1. A customer sends a message: "Where is order #AX-771-3344?"
2. The AI looks up the order in the customer record system
3. It checks the driver's GPS location
4. If the GPS is recent enough and there are no issues with the order: it replies with a time estimate
5. If the GPS is too stale, or if the order has a problem: it passes the case to a human dispatcher with all the context already assembled

**What it doesn't do:** It cannot change deliveries, handle damage claims, process credits, or do anything billing-related. One job, done well.

---

### Deliverable 5 — System / Data Inventory
**What it is:** A plain-language map of what systems exist, what data is available, what's missing, and what's risky.

**The headline findings:**

- The customer record system (Salesforce) has a modern API — AI can connect to it cleanly
- The driver GPS app is in-house built — we don't yet know whether it exposes an interface for AI to query. **This is the single most important question to answer before building**
- The routing software runs through Citrix (a remote desktop wrapper) — AI cannot interface with it without a major infrastructure project, which is why routing automation is not recommended now
- The billing system (Aurum, built in 2008) exports data once a day to CSV files, with no ability to make real-time changes. Invoice changes require raising a ticket with a separate team and waiting 48 hours. This is a hard constraint, not a software problem

**The billing audit risk:** In the billing dispute case study included in the assessment, a team member (Sandra) applied a £170 credit via a manual workaround that left no record in the audit trail. The formal approval process exists on paper but is being bypassed. Any AI involvement in billing work must fix this pattern first, not build on top of it.

---

### Deliverable 6 — Discovery Questions
**What it is:** The specific questions that need answers before the design can be finalised — not generic "tell me about your process" questions, but questions whose answers would actually change what gets built.

**The critical questions:**
1. Does the driver GPS app have an interface other systems can connect to? (If not, the precision ETA feature cannot be built)
2. What specifically made the 2024 chatbot fail — was it the *channel* (customers didn't want a bot) or the *answers* (the bot gave wrong information)? The answer changes how the new system is designed and presented to customers
3. How often do team members bypass the formal credit approval process? Is this one person's habit or a team-wide pattern? This determines whether Phase 2 (billing support) is a software project or a governance project first
4. How stale is the GPS data in practice? One case study showed a 26-minute gap. If that's typical, the AI will need to escalate more cases than planned

**Why this matters:** A strong AI assessment surfaces its own unknowns. These questions reflect genuine gaps in the information provided, not a failure to do the work.

---

### Deliverable 7 — CLAUDE.md (Project File for Developers)
**What it is:** A working file that tells an AI coding assistant exactly how to build the ETA agent — what it can and cannot do, where the safety boundaries are, and what questions need answering before certain parts can be built.

**Why it matters for the business:** This file enforces the design decisions from Deliverables 1–6 in a format that a developer picks up and follows. It prevents scope creep (the agent is ETA-only, full stop), ensures safety rules are coded in from day one (never give an ETA if the GPS is more than 60 minutes stale), and flags the parts of the build that are blocked until open questions are answered. It is the mechanism that stops "everything is fully agentic" from creeping back in during development.

---

## The honest version of the ROI story

Sarah's CEO heard a competitor saved £1.2M using AI on customer service. Before accepting that as the benchmark, it is worth being precise about what Phase 1 of this proposal actually delivers — and what the gap is.

**What Phase 1 delivers:**

The ETA agent handles roughly 70% of the 400 "where is my delivery?" inquiries per day autonomously. That releases approximately 1,120 person-minutes per day — the equivalent of about 2.5 full-time agents' worth of handling capacity.

In financial terms: a fully-loaded customer operations agent (salary, employer NI, pension, overhead) costs approximately £33,000 per year in Birmingham. 2.5 FTE equivalent = **roughly £82,500 per year in released capacity value**.

That is not £1.2M. It does not need to be, for Phase 1. But it is a real number, and it is an honest one.

**The gap with £1.2M:**

The competitor's £1.2M saving almost certainly came from one or more of the following: automating inbound across multiple work streams simultaneously (not just ETA), reducing headcount rather than redeploying capacity, or starting from a more modern system baseline that allowed broader automation from day one.

Apex's current system maturity — a 2008 billing system with no real-time API, a routing tool locked behind Citrix, and an in-house driver app whose backend API has not yet been confirmed — caps what can be automated in the near term. Promising £1.2M without fixing those constraints is how Apex's previous two projects ended.

**The full programme picture:**

Phase 1 (ETA agent): ~£82,500/year in released capacity value.

Phases 1–3 combined (ETA + billing dispute triage + exception context assembly, once prerequisites are met): potentially £200,000–300,000/year in combined capacity value.

The gap between that and £1.2M should be named openly with the CEO. The question to ask is: what specifically did the competitor automate, and what was their system baseline? That conversation is better to have now than after Phase 1 is built and the CEO asks why the numbers don't match.

**What Phase 1 is:**

An ETA lookup agent for one question, with a clean handoff to a human whenever the data is insufficient. It is not a chatbot. It is narrow, testable, and demonstrable within months. That is what a working AI programme looks like at this stage of Apex's system maturity — and it is the foundation on which the rest of the programme is built.

---

## What happens next

1. **Confirm Driver App API** — this is the one gate-blocking question before any build begins
2. **Fix the billing credit audit trail** — this must be resolved before any AI touches the billing workflow
3. **Update the Exception SOP** — Section 4.3 (damaged consignments) is blank; the team needs a documented protocol before any AI can assist with exception triage
4. **Build Phase 1 (ETA agent)** — narrow, testable, demonstrable
5. **Review and expand** — based on Phase 1 results, calibrate the scope of Phase 2 (billing dispute triage)
