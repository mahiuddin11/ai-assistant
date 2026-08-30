# Roadmap

This document defines the **order, timeline, and dependency structure** of development. Full technical specifications for each version — including testing and security checklists — are the canonical responsibility of [`requirements.md`](requirements.md); this document summarizes goals and completion criteria for sequencing purposes only.

---

## How to Read This Roadmap

Each version is a **self-contained release unit**: at completion, the system is stable, deployable, and tested. Versions are numbered to map directly to the V1/V2 source architecture documents, so implementation teams can go from architecture spec to code without re-deriving structure.

---

## Phase Summary

### Foundation — Infra Baseline
**Duration:** 3–4 weeks · No user-facing features (pure infrastructure)
**Goal:** Establish a secure, automated, observable base platform for all future development.
**Completion:** A "hello world" service deploys from commit to Kubernetes through CI/CD with no manual steps, with logs/metrics visible in Grafana.

### v1.0 — MVP (Conversational Core)
**Duration:** 6–8 weeks
**Goal:** A single-agent, text-based conversational assistant with basic memory and coarse-grained permissions, proving the end-to-end pipeline.
**Completion:** A real user signs up, asks a web-search-requiring question, gets a correct answer, and the system recalls relevant context in a later session — all permission-gated and audited.

### v1.1 — Voice Pipeline
**Duration:** 5–6 weeks · Requires v1.0
**Goal:** Add voice interaction to the proven text-chat core.
**Completion:** A user asks a question by voice, gets a real-time transcription and spoken response, and can barge in with a new command mid-response.

### v1.2 — Multi-Agent Core + Tool/Plugin Framework
**Duration:** 7–8 weeks · Requires v1.0
**Goal:** Transition from single-agent to Orchestrator-Worker multi-agent architecture; establish an MCP-compatible, sandboxed tool/plugin framework.
**Completion:** A complex request is split by the Orchestrator across two agents that collaboratively produce a correct solution.

### v2.0 — Computer Control + Permission Hardening + Security
**Duration:** 8–10 weeks · Requires v1.2
**Goal:** Enable safe computer-level action, and establish a full-grade granular permission/security stack.
**Completion:** A voice command to delete old files triggers a dry-run preview, confirmation, execution, and rollback — fully audit-logged.

### v2.1 — Emotion Detection + Automation Engine
**Duration:** 6–7 weeks · Requires v1.1 + v1.2 (parallelizable with v2.0)
**Goal:** Add emotion-sensitive response and user-defined automation rules.
**Completion:** The system adapts tone to detected frustration; a voice-created automation rule executes safely on schedule.

### v3.0 — Learning System + Memory Maturity (V1 Complete)
**Duration:** 7–8 weeks · Requires v2.0 + v2.1
**Goal:** Complete the remaining V1 architecture — memory maturity and basic learning. This is the first **commercially-viable-candidate** version ("V1.0 GA").
**Completion:** The complete V1 architecture is implemented; the system is internal-beta/soft-launch-ready.

### v3.1 — AI-OS Core (V2 Foundation)
**Duration:** 8–10 weeks · Requires v3.0 (V1 GA) complete
**Goal:** Establish a central "kernel" layer enabling all future capability growth without core-code changes. **This is an architectural milestone, not a new user feature.**
**Completion:** Every existing V1 feature routes through the AI-OS Core with zero user-visible change or downtime; a test capability is discoverable without a code deploy.

### v4.0 — Skill Framework + Project Workspace
**Duration:** 8–9 weeks · Requires v3.1
**Goal:** Introduce reusable "skills" and long-lived project containers.
**Completion:** A user creates a Workspace, invokes a system skill successfully, and conversationally teaches a new reusable custom skill.

### v4.1 — Personality Engine
**Duration:** 4–5 weeks · Requires v3.1 (parallelizable with v4.0)
**Goal:** Launch a consistent, customizable system personality.
**Completion:** A configured persona is reflected consistently across all agents/skills, with temporary emotional adaptation but a stable core.

### v5.0 — Long-Term Learning + Multi-Agent Collaboration + Daily Assistant
**Duration:** 10–12 weeks · Requires v4.0 · **Needs substantial real-usage data — schedule after soft-launch/beta**
**Goal:** Deeper long-term intelligence, sophisticated agent collaboration, and proactivity.
**Completion:** Multiple agents debate a high-stakes/ambiguous decision to consensus or human escalation; the user receives a relevant daily briefing; the system suggests new automations/skills from detected patterns.

### v5.1 — Governance Layer
**Duration:** 8–10 weeks · Requires v4.0 + a meaningful portion of v5.0's real-usage data
**Goal:** Establish institutional policy, compliance, and formal human-review workflows — a prerequisite for commercial/enterprise readiness.
**Completion:** A compliance officer sets an org-level policy, the system auto-enforces it, and a human-readable explanation is available for any decision.

### Commercial Release (GA)
**Duration:** 6–8 weeks · Requires v5.1 complete
**Goal:** Convert the product into a publicly sellable, SLA-backed, multi-tenant commercial service.
**Completion:** Public sign-up is open; the first paying customer subscribes, uses, and is billed within published SLAs, after an independent security audit.

### Enterprise Edition (Optional, Post-GA)
**Duration:** 10–14 weeks · Requires Commercial GA stable
**Goal:** Deliver a high-control, self-hostable, deeply-compliant version for large organizations.
**Completion:** An enterprise client deploys on its own infrastructure, logs in via its own SSO, activates an industry-specific compliance pack, and exports an audit report.

---

## Cumulative Timeline

*(Assumes a sequential build with a 5–7 engineer team.)*

| Version | Duration | Cumulative Time | Key Milestone |
|---|---|---|---|
| Foundation | 3–4 weeks | Week 4 | Infra ready |
| v1.0 MVP | 6–8 weeks | Week 12 | First end-to-end conversation |
| v1.1 Voice | 5–6 weeks | Week 18 | Voice interaction live |
| v1.2 Multi-Agent + Plugin | 7–8 weeks | Week 26 | Multi-agent task solving |
| v2.0 Computer Control + Security | 8–10 weeks | Week 36 | Safe system-level actions live |
| v2.1 Emotion + Automation | 6–7 weeks | Week 43 | Adaptive + automated assistant |
| **v3.0 (V1 GA)** | 7–8 weeks | **Week 51 (~1 year)** | **V1 architecture complete — Internal Beta** |
| v3.1 AI-OS Core | 8–10 weeks | Week 61 | Central kernel live, no feature breakage |
| v4.0 Skill + Workspace | 8–9 weeks | Week 70 | Skill ecosystem launched |
| v4.1 Personality | 4–5 weeks | Week 75 | Personality-equipped assistant |
| v5.0 Learning + Collab + Daily | 10–12 weeks | Week 87 | Proactive, self-improving system |
| v5.1 Governance | 8–10 weeks | Week 97 | Enterprise-ready governance |
| **Commercial GA** | 6–8 weeks | **Week 105 (~2 years)** | **Public paid launch** |
| Enterprise Edition (Optional) | 10–14 weeks | Week 119+ | On-prem/enterprise contract-ready |

> This timeline assumes sequential development. With a larger team, some versions can run **in parallel** — see the matrix below.

---

## Dependency & Parallelization Matrix

| Version | Hard Prerequisite | Can Run in Parallel? |
|---|---|---|
| v1.1 Voice | v1.0 MVP | No — depends on core conversation logic |
| v1.2 Multi-Agent | v1.0 MVP | Partially parallel with v1.1 (separate sub-team) |
| v2.0 Computer Control | v1.2 (agent architecture) | No — depends on agent framework |
| v2.1 Emotion + Automation | v1.1 (Voice) + v1.2 (Agent) | Yes, parallel with v2.0 |
| v3.0 Learning/Memory | v2.0, v2.1 | No — depends on all interaction data sources |
| v3.1 AI-OS Core | v3.0 (V1 GA) complete | No — wraps V1, which must be stable first |
| v4.0 Skill + Workspace | v3.1 AI-OS Core | Parallel with v4.1 Personality |
| v4.1 Personality | v3.1 AI-OS Core (needs Context Manager) | Yes, parallel with v4.0 |
| v5.0 Learning + Collab + Daily | v4.0 (needs Skill/Workspace data) | Partial — Daily Assistant can start earlier than the rest |
| v5.1 Governance | v4.0 + partial v5.0 (sufficient data patterns) | No — needs enough real-usage data for meaningful policy |
| Commercial GA | v5.1 Governance complete | No — commercial launch without compliance/governance is high-risk |
| Enterprise Edition | Commercial GA stable | Yes, can start as a post-GA parallel track |

**Never parallelize:** v2.0 before v1.2; v3.0 before v2.0/v2.1; v3.1 before v3.0 (V1 GA); v5.1 before sufficient real-usage data exists; Commercial GA before v5.1 Governance.

---

## Release-Gate Policy

Before advancing from any version to the next, **all four gates** below must pass. This is the canonical release-gate definition referenced by [`requirements.md`](requirements.md) and [`development-plan.md`](development-plan.md).

1. ✅ **All testing checklist items** for that version pass (see `requirements.md`).
2. ✅ **All security checklist items** for that version pass, with no open critical/high-severity finding (see `requirements.md`).
3. ✅ **Completion criteria** are demonstrably shown (live demo or recorded proof).
4. ✅ **Regression**: all previous versions' completion criteria still hold — nothing has broken.

No version's development should begin until the prior version (per the dependency matrix above) has passed all four gates.