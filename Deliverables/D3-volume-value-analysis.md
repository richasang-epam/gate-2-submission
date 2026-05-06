# Deliverable 3 — Volume × Value Analysis

> **Apex context:** See [_shared-context.md](_shared-context.md)  
> **Delegation archetypes (informing automation ceiling):** See [D2-delegation-suitability-matrix.md](D2-delegation-suitability-matrix.md)

---

## Axes

**Volume (X-axis):** Cases per day — observable from scenario brief.

**Value (Y-axis):** Composite of:
1. **Effort consumed** — daily person-minutes (volume × avg handling time)
2. **Automatable fraction** — % of that effort that could be delegated to an agent (informed by D2 archetypes)
3. **Data quality for automation** — availability and reliability of the data needed
4. **Risk of automation** — consequence of error, system fragility, compliance exposure

Value is not just "most minutes consumed" — it is the intersection of effort, automation ceiling, and risk.

---

## Work Stream Plot Data

| Work Stream | Volume/Day | Handling Time | Daily Minutes | Automatable % | Daily Mins Recoverable | Data Quality | Risk Level |
|---|---|---|---|---|---|---|---|
| ETA Inquiries | **400** | 4 min | 1,600 | **~70%** | **~1,120** | High (CRM API + GPS) | Low |
| Delivery Exceptions | 180 | 12 min | 2,160 | ~25% | ~540 | Medium (SOP incomplete) | High |
| Dispatch Adjustments | 90 | 18 min | 1,620 | ~15% | ~243 | Low (Citrix barrier) | Very High |
| Billing Disputes | 60 | 28 min | 1,680 | ~35% | ~588 | Low (Aurum batch-only) | High |

*Automatable % is the agent-addressable fraction of handling time based on D2 archetypes and zone maps from D1. It is not the full handling time — only the agent-reachable portion.*

---

## Quadrant Map (conceptual — text representation)

```
HIGH VALUE
    |
    |   [ETA Inquiries]              ← Primary target
    |   Volume: HIGH / Value: HIGH
    |   (high volume, high automation ceiling, low risk)
    |
    |                    [Billing Disputes]
    |                    Volume: LOW / Value: MEDIUM
    |                    (constrained by Aurum, but meaningful triage value)
    |
    |   [Delivery Exceptions]
    |   Volume: MEDIUM / Value: MEDIUM
    |   (high effort, but low automation ceiling)
    |
    |                    [Dispatch Adjustments]
    |                    Volume: LOW / Value: LOW (near-term)
    |                    (Citrix barrier = not accessible yet)
    |
LOW VALUE
    |_____________________________________________
    LOW VOLUME                         HIGH VOLUME
```

---

## Primary Agentic Target: ETA Inquiries

**Justification:**

**1. Highest volume, lowest cognitive load.**  
400 cases/day represents 55% of all Customer Operations cases. The workflow is structured: lookup → interpret → respond. Artefact 3 confirms the standard case is a 2-step data retrieval (CRM + GPS) that produces a deterministic answer. The cognitive load analysis in D1 shows the standard case has low working memory demand, low judgment requirement, and low emotional labour.

**2. Best data availability.**  
Salesforce CRM has a confirmed REST API. The Driver App provides GPS telemetry (assumed REST API — discovery question in D6). No legacy system dependency for the standard ETA case. The data pipeline is already partially in place.

**3. Lowest risk of automation errors.**  
A slightly incorrect ETA estimate is recoverable: the customer gets an update when the driver is closer. This contrasts sharply with billing disputes (financial impact), delivery exceptions (operational failure), and dispatch adjustments (multi-vehicle cascade). Low consequence of error = safe to start here.

**4. Fastest path to visible results.**  
Sarah Whitmore needs a win that is visible and different from the failed chatbot and failed RPA project. An ETA agent that answers "Where is my order?" in under 2 minutes (vs current 4+ minutes, with manual dispatch check) is immediately demonstrable. It does not touch Aurum. It does not require Citrix integration. It is buildable on the existing API surface.

**5. Estimated impact — capacity and financial.**

*Capacity:* ~1,120 recoverable person-minutes/day ≈ 18.7 person-hours/day. Annualised at 48 working weeks × 5 days: ~4,488 person-hours/year ≈ **2.5 FTE-equivalent handling capacity**.

*Financial value of released capacity:* A customer operations agent in Birmingham costs approximately £26,000/year in salary. Adding employer NI (~£2,300), employer pension (3%, ~£780), and a conservative 15% overhead allocation (IT, HR, facilities: ~£3,900) gives a **fully-loaded cost of ~£33,000/year per agent**. 2.5 FTE equivalent = **~£82,500/year in released capacity value**.

*Important caveats on this figure:*
- This is released capacity, not guaranteed cash savings. Apex's 35-person team handles 730 cases/day — the intention is redeployment into higher-judgment work (Exceptions, Billing) rather than headcount reduction.
- If the team is at capacity today, the real value is absorbing demand growth or improving SLA compliance on Exceptions and Billing without adding headcount — harder to quantify but real.
- The CEO's £1.2M competitor benchmark almost certainly reflects broader scope: full inbound automation across multiple work streams, or headcount reduction rather than redeployment, or a more modern system baseline enabling wider automation. Phase 1 (ETA only) at ~£82,500/year does not match £1.2M, and presenting it as equivalent would be dishonest. The full phased programme (Phases 1–3: ETA + billing triage + exception context assembly) might reach £200,000–300,000/year in combined capacity value — still below £1.2M, because Apex's system maturity (Aurum batch-only, Citrix dispatch, unconfirmed Driver App API) caps what is automatable in the near term. See D6 Q9 for how to surface this expectations gap constructively with Sarah's CEO.

---

## Secondary Target: Billing Disputes (Triage + Communication Layer)

**Justification for secondary (not primary):**

Billing disputes are the highest-value case per incident (28 min avg, £340+ disputed amounts in the artefacts) and carry relationship risk — Hayes & Sons (C-04451) has 3 disputes logged in Q1 2026 alone, suggesting a systemic issue, not isolated events.

However, the Aurum constraint is a hard ceiling. An agent cannot:
- Retrieve real-time invoice data (T-1 batch minimum)
- Adjust fuel surcharge line items (Aurum design limitation)
- Apply credits without a 48h manual ticket (for invoice-level modifications)

What an agent CAN do in the dispute workflow:
- Parse the incoming dispute (type, invoice reference, customer)
- Retrieve the relevant invoice, surcharge, and credit records from the T-1 batch
- Cross-reference dispute history from APEX_DISPUTES_OPEN
- Draft a factually accurate response for human review
- Stage a credit proposal for human approval via the formal APPROVER_ID + AUDIT_REF pathway
- Flag repeat patterns (e.g., Hayes & Sons recurring FUEL_SURCH_DAMAGE) for account review

**Prerequisite:** The manual override / audit bypass pattern (Sandra, Artefact 2) must be addressed before an agent operates in this workflow. Automating on top of a broken audit trail compounds, not fixes, the control gap.

---

## Why Dispatch Adjustments is Not the Target

Dispatch Adjustments scores third on raw effort (1,620 min/day) but is the least accessible of the four work streams:
- Citrix-deployed Dispatch Console with "limited API surface" = no clean agent integration
- Highest error consequence of any work stream (multi-vehicle, real-time cascade)
- Shortest decision window (mid-route, seconds-to-minutes)

This work stream requires a Dispatch Console re-platforming decision before agent automation becomes viable. It is the right long-term target but the wrong place to start.

---

## Sequencing Recommendation

| Phase | Target | Dependency | Expected Timeline |
|---|---|---|---|
| **Phase 1** | ETA Inquiries Agent | Driver App API confirmation; Salesforce schema | Buildable now |
| **Phase 2** | Billing Dispute Triage Agent | Fix audit trail enforcement; Aurum batch pipeline built | After Phase 1 stable |
| **Phase 3** | Delivery Exception Context Assembly | SOP updated; insurance protocol documented | After Phase 2 |
| **Phase 4** | Dispatch Adjustments | Dispatch Console API re-platform | Multi-year; separate project |
