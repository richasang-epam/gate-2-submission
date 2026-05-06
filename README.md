# Gate 2 — Richa Sang
**ATX Methodology | Apex Distribution Ltd — Customer Operations Agentic Transformation**

---

## What this is

This is a Gate 2 submission for the ATX (Agentic Transformation) methodology programme. The scenario is Apex Distribution Ltd, a regional B2B/DTC carrier based in Birmingham, UK. The brief asks whether and how AI agents can safely take over parts of their Customer Operations function.

The short answer: one work stream qualifies for agent-led handling on day one. Three others need human judgment that no agent can safely replace yet. The submission explains why, and constrains the one that does qualify hard enough that it can't cause the failures Apex has already lived through.

---

## Submission document

**[Gate2-Richa-Sang.md](Gate2-Richa-Sang.md)** — the master submission. Self-contained, all seven deliverables in one document. This is the file coaches review.

---

## Seven deliverables

| # | File | What it answers |
|---|---|---|
| D1 | [Deliverables/D1-cognitive-load-map.md](Deliverables/D1-cognitive-load-map.md) | What do humans actually do in each work stream — not what the SOP says |
| D2 | [Deliverables/D2-delegation-suitability-matrix.md](Deliverables/D2-delegation-suitability-matrix.md) | Which work streams can be delegated to an agent, scored and ranked |
| D3 | [Deliverables/D3-volume-value-analysis.md](Deliverables/D3-volume-value-analysis.md) | Where the automation value is, and why the MVP wasn't chosen for savings |
| D4 | [Deliverables/D4-agent-purpose-document.md](Deliverables/D4-agent-purpose-document.md) | Full spec for the ETA agent: scope, autonomy rules, escalation triggers, governance |
| D5 | [Deliverables/D5-system-data-inventory.md](Deliverables/D5-system-data-inventory.md) | Every system mapped with availability, risk, and integration constraints |
| D6 | [Deliverables/D6-discovery-questions.md](Deliverables/D6-discovery-questions.md) | Eleven questions that would materially change what gets built |
| D7 | [Deliverables/CLAUDE.md](apex-eta-agent/CLAUDE.md) | Working instruction file for an AI coding agent — the live project constraints |

---

## Working prototype

**[apex-eta-agent/](apex-eta-agent/)** — a runnable Flask implementation of the ETA agent described in D4.

### What it does

Handles inbound "where is my delivery?" enquiries end-to-end. Applies a 9-rule decision engine to determine whether to respond autonomously, respond with caveats, or escalate — and to whom.

```
Inbound query
    → resolve order (Salesforce CRM)
    → get GPS (Driver App)
    → check open disputes
    → evaluate autonomy mode
    → compose response OR route escalation
    → log CRM case
```

### Four outcomes

| Mode | Condition | What happens |
|---|---|---|
| **Autonomous** | GPS <30 min, no flags | Agent responds with ETA window; logs case |
| **Supervised** | GPS 30–60 min | Widened window + staleness disclosure; flagged for review |
| **Escalate → Dispatcher** | GPS >60 min or Driver App offline | Context pre-populated; routed to dispatch |
| **Escalate → Human Agent** | Exception, dispute, missing parcel, strategic account | Routed to appropriate human queue |

### Run it

```bash
cd apex-eta-agent
start.bat          # Windows — installs deps, starts server on http://localhost:5000
```

Or manually:

```bash
pip install -r requirements.txt
python run.py
```

### Run the tests

```bash
cd apex-eta-agent
python -m pytest tests/ -v
```

16 tests, covering all escalation rules including boundary conditions and the strategic account trigger (Escalation Trigger 9, validated from APEX_CUSTOMER_MASTER).

### Demo scenarios

The mock data covers all four decision modes across eight real-looking orders:

| Order | Customer | Trigger | Expected mode |
|---|---|---|---|
| AX-771-3344 | Morrison Catering Ltd | GPS 8 min — clean | **AUTONOMOUS** |
| AX-330-7761 | Redstone Facilities | GPS 38 min — degraded | **SUPERVISED** |
| AX-443-8812 | TechHub Birmingham | GPS 72 min — stale | **ESCALATE → Dispatcher** |
| AX-882-1105 | Bridgewater Hotels Group | CRM exception flag | **ESCALATE → Human** |
| AX-554-9921 | Hayes & Sons | Open dispute + strategic account | **ESCALATE → Human** |
| AX-667-2290 | Quantum Logistics UK | Delivered, no scan event | **ESCALATE → Human (urgent)** |
| AX-990-5544 | Aston Medical Supplies | Driver App exception flag | **ESCALATE → Human** |
| AX-119-4480 | Parkside NHS Trust | GPS 26 min — clean | **AUTONOMOUS** |

---

## Presentation

**[Gate2-Richa-Sang-Presentation.pptx](Gate2-Richa-Sang-Presentation.pptx)** — slide deck built from [Presentation/build_pptx.py](Presentation/build_pptx.py).

To regenerate after any content change:

```bash
cd Presentation
python build_pptx.py
```

---

## Design decisions worth noting

**Why ETA inquiries and not a higher-value work stream:** ETA is the only work stream where an agent error is recoverable. Wrong exception disposition cascades to routes, depots, and customers. Wrong billing credit has financial and audit consequences. Wrong dispatch adjustment can be irreversible within a shift window. Blast radius, not savings, drove the MVP choice.

**Why the SOP was treated as low-confidence:** SOP v2.3 references DispatchHub, retired October 2024. Section 4.3 (damaged consignments) is blank. Anything built against the SOP as ground truth fails on the exact edge cases the team has already silently adapted to.

**Why adoption failure is treated as a first-class risk:** Apex has had two automation failures — a customer chatbot and an RPA billing project. A technically correct agent that dispatchers bypass is operationally equivalent to a third failure. The governance model, rollback conditions, and organisational rejection risk table in D4 exist because of this, not despite it.

---

## Repository structure

```
gate-2-submission/
├── Gate2-Richa-Sang.md              # Master submission (coaches read this)
├── Gate2-Richa-Sang-Presentation.pptx
├── Deliverables/
│   ├── D1-cognitive-load-map.md
│   ├── D2-delegation-suitability-matrix.md
│   ├── D3-volume-value-analysis.md
│   ├── D4-agent-purpose-document.md
│   ├── D5-system-data-inventory.md
│   └── D6-discovery-questions.md
|   ├── D7-CLAUDE.md                    # D7 — AI coding agent constraints
├── apex-eta-agent/                  # Runnable prototype
│   ├── app/agent/                   # Core pipeline modules
│   ├── mock_data/                   # Orders, GPS positions, disputes
│   ├── templates/ + static/         # Dashboard UI
│   ├── tests/                       # 16 unit tests
│   └── start.bat
└── Presentation/
    └── build_pptx.py                # Slide deck generator
```
