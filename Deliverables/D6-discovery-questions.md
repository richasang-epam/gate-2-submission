# Deliverable 6 — Discovery Questions for the Main Stakeholder

> **Assumptions these questions would resolve:** See [D5-system-data-inventory.md](D5-system-data-inventory.md)  
> **Design decisions these answers would change:** noted per question below

These are questions whose answers would materially change the design — not "tell me about your process" questions. Each question is tied to a specific tension or gap identified in the artefacts and brief.

---

## Tier 1: Design-Blocking (answers change architecture)

### Q1 — Driver App API
> *"The ETA agent I'm designing depends on querying the Driver App for GPS data. The brief says the app is in-house. Does the backend expose an API that other systems can query, or does the dispatch team interact with it only through the web console? I'm asking because if there's no API, the GPS integration phase has no foundation — I need to know this before we scope the build."*

**Why this matters:** If the Driver App backend has no external API, the ETA agent can only provide the CRM-held delivery window (4-hour standard window), not a narrowed GPS-based estimate. That halves the value proposition for customers. The answer changes whether Phase 1 is viable as designed or needs a prerequisite infrastructure sprint first.

**Evasion signal to watch:** "I'd have to ask IT." → Press: "Is there a tech lead I could speak with for 30 minutes before we start the build? The whole GPS phase depends on this."

---

### Q2 — The chatbot failure root cause
> *"You mentioned the 2024 chatbot customers hated. I want to understand whether it was the channel (customers didn't want a bot), the answer quality (bot gave wrong or useless answers), or the scope (it tried to handle too much and failed on edge cases). I'm asking because the ETA agent I'm proposing has some surface similarity to a chatbot — it responds automatically — and I need to know which failure mode to design against."*

**Why this matters:** If customers hated the chatbot because they wanted a human (channel aversion), the ETA agent needs a visible and easy "talk to a person" escape hatch from first contact. If it failed on answer quality, the staleness and escalation logic in the autonomy matrix is the key safeguard to emphasise. If it tried to do too much, the narrow scope of the ETA agent (ETA only, no exceptions, no billing) is the differentiator to make explicit to Sarah's team and customers.

**Evasion signal:** "It just wasn't good." → Press: "Did customers complain about talking to a bot, or about the answers it gave them? Those require different fixes — that distinction matters for what I build."

---

### Q3 — Credits audit trail and approval authority
> *"In the Artefact 2 email thread, there's an internal note saying Sandra applied a £170 goodwill credit with no entry in the credits audit log — a manual override. I can see the formal APPROVER_ID and AUDIT_REF fields in the credits CSV exist. How common is this pattern — agents applying credits outside the formal pathway? And who has the authority to approve a credit above, say, £100?"*

**Why this matters:** The billing dispute triage agent I'm scoping for Phase 2 would stage credits for human approval — but only if the approval pathway is actually used. If agents routinely bypass the formal pathway, building an agent that uses it will either be ignored or create conflict. The answer changes whether the billing phase is a "build the agent" problem or a "fix the process governance first" problem. The second is harder and slower.

**Evasion signal:** "That's a one-off." → Press: "The disputes CSV shows C-04451 has three open FUEL_SURCH_DAMAGE disputes and the credits CSV shows a prior goodwill credit for the same customer on a different invoice. Is this specifically Sandra, or is it a broader pattern across the team?"

---

### Q4 — GPS lag in production
> *"The SMS artefact shows the driver's last GPS ping was 26 minutes before the agent responded. Is that typical — GPS data being that stale in production — or was that an unusual day? I need to know the realistic GPS latency to set the right staleness thresholds in the agent's logic."*

**Why this matters:** The staleness threshold (30 min / 60 min) in the autonomy matrix is based on an assumption. If GPS data is routinely 20–30 minutes stale, the 30-minute threshold will escalate 30–40% of cases instead of the planned 20%. That changes the staffing model for human dispatcher coverage. If 26 minutes is unusual, the threshold is fine as-is.

**Evasion signal:** "It varies, honestly." → Press: "If you had to guess: in a typical day, what fraction of your ETA inquiries require an agent to call dispatch because the GPS window is too wide to be useful? Even a rough estimate helps."

---

## Tier 2: Scope-Defining (answers refine the design)

### Q5 — ETA inquiry channel breakdown
> *"The brief gives 400 ETA inquiries per day but doesn't break down by channel. Roughly what proportion come in via SMS, email, phone, and — if you have a web portal — there? The build scope for the agent changes significantly if we're handling two channels versus four."*

**Why this matters:** Each channel requires a different integration (SMS webhook, email parser, web API). A 400/day SMS-only agent is a different build to a 400/day omnichannel agent. The answer also reveals whether there's a self-service tracking page already (a common carrier feature) that could handle the simple lookups without a new agent at all.

---

### Q6 — Billing disputes: active time vs elapsed time
> *"Billing disputes average 28 minutes handling time. Is that 28 minutes of active agent work, or 28 minutes of elapsed time including waiting — for a callback, for Aurum to load, for a manager to approve? I'm asking because if the agent spends 5 minutes of active work and waits 23 minutes for a system, the automation opportunity is very different."*

**Why this matters:** If 80% of billing dispute time is waiting on Aurum loads or approval callbacks, an agent that eliminates that waiting (by pre-pulling the data) could reduce handling time dramatically even without touching Aurum's write-path. If it's 28 minutes of active decision-making, the scope of useful automation is much narrower.

---

### Q7 — Sandra's authority and the broader team structure
> *"In the email thread, Sandra seems to be the go-to for billing disputes — she handled the Hayes & Sons case, and I can see she's assigned to multiple open disputes in the data. Is exception handling and billing dispute work concentrated in a few named agents, or is it distributed across the team? And is there a Duty Manager role that's currently active on each shift?"*

**Why this matters:** If exception handling and billing disputes are concentrated in 2–3 named experts (Sandra-type agents), the agent design needs to work *with* those people — surfacing context and drafting communications for their review — not route around them. If work is distributed, the escalation routing logic is different. The Duty Manager question is relevant because SOP 4.2 requires escalation to Duty Manager for high-value consignments — if that role is understaffed or informal, the escalation path doesn't work.

---

### Q8 — The SOP gap
> *"Section 4.3 of the SOP — damaged consignments — is blank: 'TBD pending review of insurance protocol.' The SOP was last revised October 2023. It also still references DispatchHub, which was retired in 2024. Is the SOP being updated, or has the team effectively moved to informal knowledge for exception handling? I'm asking because the exception context-assembly agent I'm scoping for Phase 3 needs an actual protocol to surface — not a placeholder."*

**Why this matters:** If SOP 4.3 is still blank and the team has no insurance protocol, the exception agent in Phase 3 cannot safely surface "what to do about damage" — it would be amplifying the absence of a rule. The answer either gates Phase 3 on an SOP rewrite or confirms the agent needs to surface human judgment explicitly rather than protocol.

---

### Q9 — Competitor context
> *"Your CEO mentioned a competitor saving £1.2M annualised on customer service with AI. Do you have any detail on what they actually changed — was it inbound volume reduction, headcount redeployment, or something else? I'm not asking to copy them; I'm asking because the £1.2M number will come up in your internal approvals, and your CEO will expect a comparable ROI framing. I want to make sure my estimate is defensible."*

**Why this matters:** The answer either validates or pressures the £1.2M framing. If the competitor automated full inbound handling (not just ETA), Sarah's CEO may expect a broader scope than Phase 1 delivers. Better to surface that expectation gap now than after Phase 1 is built.

---

## Tier 3: Constraint-Validating (answers confirm or invalidate design assumptions)

### Q10 — Contractual SLAs and breach tracking
> *"Are there contractual SLAs with B2B customers governing exception resolution or billing dispute turnaround times? The Hayes & Sons thread shows 9 days between initial contact and resolution — is that a breach, and is breach status tracked in Salesforce or Aurum?"*

**Why this matters:** If SLAs are tracked in Salesforce, breach status becomes a priority signal in exception context pre-assembly — cases near or past breach route differently. If SLAs exist but are untracked, SLA tracking becomes a prerequisite for priority-weighted escalation design. If SLAs don't exist, the Hayes & Sons pattern is a relationship management issue, not a compliance one, changing escalation urgency framing.

---

### Q11 — Salesforce customer-tier or key-account flag
> *"Does Salesforce carry a customer-tier, key-account, or commercial-sensitivity flag? The Stein-Allen account was treated as high-value by the dispatcher — that weighting shaped the exception decision. If AERA gives the same automated response to Stein-Allen as to a single-parcel DTC customer, we're eliminating a differentiation that currently exists. I want to know if that data is already in Salesforce, or whether it's dispatcher memory."*

**Why this matters:** If flag exists → add strategic account escalation trigger before launch. If no data → data gap requiring remediation before launch.

`[VALIDATED — Gate 2 Artifacts]` APEX_CUSTOMER_MASTER confirms ACCT_MGR field. Hayes & Sons (C-04451) assigned to U-0089 (Sandra W.). Escalation Trigger 9 in D4 is build-ready. This question is now confirmatory, not exploratory.

---

## For the Live Round: Detecting Evasion

| If Sarah says... | It may mean... | Press with... |
|---|---|---|
| "The chatbot was just bad" | Hasn't analysed the failure mode | "Was it what it said, or that it was a bot at all?" |
| "The RPA project was the vendor's fault" | Avoiding the Aurum schema-change reality | "Did Aurum's schema change without notice? That's a design constraint I need to know about, not a blame question." |
| "Credits are handled by the team" | Doesn't know the audit bypass is happening | "Are you aware that credits can be applied via manual override without entering the audit log? Is that sanctioned?" |
| "The Driver App team will sort the API out" | No API exists yet / vague promise | "So there's no API today. What's the timeline, and is that a dependency that would gate the ETA build?" |
| "We'd have to check the exact numbers" | Doesn't track channel breakdown or GPS latency metrics | "That's fine — is there someone in your team who runs analytics I could speak with after this session?" |
