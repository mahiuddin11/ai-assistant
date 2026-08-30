# Architecture Decision Records (ADRs)

This document records the key design decisions embedded in the project's architecture and roadmap, in ADR format: **Status → Context → Decision → Consequences.** These decisions are extracted and structured from the source architecture and roadmap documentation — no new decisions are introduced here.

---

## ADR-001: Every Version Is a Self-Contained Release Unit

**Status:** Accepted

**Context:** The roadmap spans roughly two years of sequential development across fourteen versions. A purely "big bang" development model would leave the system unshippable for extended periods and make it hard to validate progress.

**Decision:** Every version, from Foundation through Enterprise Edition, must leave the system in a stable, deployable, tested state at completion, with its own testing checklist, security checklist, and completion criteria.

**Consequences:**
- The team can stop at any completed version and ship a stable product without waiting for later milestones.
- Each version requires its own full testing and security pass, increasing per-version overhead but reducing integration risk.
- Regression testing against all prior completion criteria is required at every release gate.

---

## ADR-002: V1 Monolithic Kernel First, Then Non-Breaking V2 Wrap

**Status:** Accepted

**Context:** The platform needs to grow substantially in capability (skills, workspaces, personality, long-term learning, governance) without repeatedly rewriting its core.

**Decision:** Build a complete, independent product first (V1 Architecture Line, Foundation → v3.0). Then introduce a central "kernel" layer — the AI-OS Core (v3.1) — that wraps the existing V1 Orchestrator as a "planning module" inside a new Central Dispatch, rather than replacing it.

**Consequences:**
- v3.1 requires a full backward-compatibility regression suite verifying every V1 feature still works, unchanged, once AI-OS Core is live.
- All capability growth after v3.1 (skills, personality, collaboration, governance) is registered through the Capability Registry rather than hardcoded into the core.
- v3.1 must not begin until v3.0 (V1 GA) is complete and stable — this is treated as a hard dependency, not a parallelizable one.

---

## ADR-003: Anthropic Claude as Primary LLM Provider

**Status:** Accepted

**Context:** The system requires a single, consistent LLM backend for the conversational core, tool-calling/function-calling based reasoning, and multi-agent planning.

**Decision:** Anthropic's Claude API is designated as the primary LLM provider from the Foundation phase (account/API-key provisioning) through v1.0's conversational agent integration.

**Consequences:**
- Prompt engineering, function-calling patterns, and retry/timeout handling are designed around the Claude API's interface.
- Provider-specific integration work is concentrated in the Conversational Agent Service and later the AI-OS Core dispatch layer.

---

## ADR-004: Sandboxed Plugin/Tool Execution (WASM/gVisor)

**Status:** Accepted

**Context:** Introducing a third-party tool/plugin ecosystem (v1.2) creates a risk surface: untrusted code executing within the platform.

**Decision:** All plugins run inside a sandboxed runtime (WASM or gVisor), governed by a manifest declaring their permissions, with per-plugin resource limits and mandatory code-signing verification.

**Consequences:**
- Actions outside a plugin's declared manifest permissions must be blocked and verified via testing.
- A crashing or malicious plugin must not affect the rest of the system (isolation is a release-gate testing requirement).
- Sandbox-escape penetration testing is mandatory before v1.2 can be considered complete.

---

## ADR-005: Non-Bypassable Permission Engine and Governance Router

**Status:** Accepted

**Context:** As the system gains more autonomous capability (computer control in v2.0, multi-agent delegation in v5.0, organizational policy in v5.1), permission and policy enforcement must remain reliable even as new capabilities and delegation paths are introduced.

**Decision:** Permission checks are structurally enforced, not optional: coarse-grained in v1.0, upgraded to RBAC+ABAC in v2.0, and unified under a single Governance Router from v3.1 onward that every capability dispatch path must pass through. The v5.1 Policy Engine and Compliance Module integrate synchronously into this same router rather than creating a second, parallel enforcement path.

**Consequences:**
- Every architectural milestone from v3.1 onward includes an explicit test verifying no dispatch path can bypass the Governance Router.
- Agent-to-agent delegation (v5.0) does not imply automatic trust — every delegation re-triggers a permission check.
- Persona configuration (v4.1) and automation rules (v2.1) are explicitly required to pass through this same enforcement chain.

---

## ADR-006: Execution Broker Isolated From Agent Processes

**Status:** Accepted

**Context:** Enabling computer control (v2.0) means the system can take real, potentially destructive actions on a user's machine. If the same process that plans actions can also execute them with elevated privileges, a compromised or misbehaving agent could cause direct harm.

**Decision:** The Execution Broker is implemented as a fully separate process from the core agent/orchestration processes. No agent process is ever granted direct root/admin access; all system-level actions pass through the broker, which supports dry-run mode and rollback via execution snapshots.

**Consequences:**
- v2.0 requires a specific privilege-escalation penetration test targeting the Execution Broker.
- Every computer-control action must support a dry-run preview and a rollback path before being considered complete.

---

## ADR-007: Governance Layer Deferred Until Sufficient Real-Usage Data Exists

**Status:** Accepted

**Context:** Meaningful organizational policy (v5.1) and some long-term learning features (v5.0) depend on having real usage patterns to reason about — policies designed against no real data risk being arbitrary or ineffective, and cross-workspace pattern mining requires actual cross-workspace activity to mine.

**Decision:** v5.0 is explicitly scheduled after a soft-launch/beta user base exists, and v5.1 depends not only on v4.0 completion but on "a meaningful portion of v5.0's real-usage data." Commercial GA, in turn, is gated on v5.1 Governance being complete.

**Consequences:**
- v5.0 and v5.1 cannot be scheduled purely on engineering capacity — they have a data-readiness dependency in addition to a code dependency.
- If real-usage data is insufficient when a v5.0/v5.1 phase prompt is submitted for execution, synthetic/simulated datasets should be used for testing and production rollout should be flagged as provisional until real data is available.

---

## ADR-008: Development Executed via Google Jules Using Single-Phase-Scoped Prompts

**Status:** Accepted

**Context:** Google Jules is an asynchronous coding agent without persistent memory across sessions. Submitting the entire multi-year roadmap at once risks scope creep, out-of-order implementation, and unreviewable, unbounded pull requests.

**Decision:** Development is executed one roadmap phase at a time. Each phase is submitted as a self-contained prompt (Repo Context Block + phase-specific Objective/Tasks/Deliverables/Checklists/Completion Criteria/Stop Condition), and Jules is explicitly instructed to stop after completing that phase's scope rather than proceeding into future phases.

**Consequences:**
- Every phase produces an independently reviewable pull request, which must pass the release-gate policy before merging.
- Large phases (e.g. v1.2, v2.0, v5.0) are broken into sub-tasks that can optionally be run as separate Jules sessions/PRs.
- Future-phase functionality must not be implemented early, though code should be designed with extensible interfaces/abstractions to ease future phases.

---

## ADR-009: Per-User and Right-to-Forget Guarantees as a Baseline Requirement

**Status:** Accepted

**Context:** The system accumulates increasingly rich personal data over time — semantic memory (v1.0), voice/speaker data (v1.1), emotion tags (v2.1), episodic/procedural memory (v3.0), and cross-workspace patterns (v5.0). Privacy risk compounds with each new memory type.

**Decision:** Right-to-forget (memory deletion) and per-user/per-tenant data isolation are introduced alongside the first memory type (v1.0) and are required to remain fully functional and independently testable as every subsequent memory type is added.

**Consequences:**
- v3.0's security checklist explicitly re-verifies right-to-forget across episodic and procedural memory, not just the original semantic memory.
- v5.0's cross-workspace pattern mining is required to be privacy-preserving and per-user isolated by design, not as an afterthought.
- Emotion data (v2.1) defaults to session-scoped storage, with long-term profiling only available via explicit opt-in.

---

## ADR-010: Raw Voice Audio Is Never Persisted by Default

**Status:** Accepted

**Context:** Voice interaction (v1.1) requires processing raw audio for STT/speaker identification, but persisting raw audio indefinitely creates a substantial and often unnecessary privacy liability.

**Decision:** Raw audio is never permanently stored; only the transcribed text is retained, unless the user has explicitly opted in to raw audio retention. Voice streams are encrypted in transit (DTLS-SRTP/WSS), and speaker-identification data is scoped per-tenant.

**Consequences:**
- v1.1's security checklist requires explicit verification that raw audio is not persisted outside of the opt-in path.
- Any future feature that might want to reuse raw audio (e.g. voice-print based features) must go through the same explicit opt-in mechanism rather than assuming availability.