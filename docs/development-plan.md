markdown
# Development Plan — Google Jules Execution Playbook

This document defines **how** the roadmap in [`roadmap.md`](roadmap.md) is actually executed, using the Google Jules coding agent. It does not redefine scope or requirements — those remain canonical in [`requirements.md`](requirements.md).

---

## Execution Methodology

Google Jules is an asynchronous coding agent: it takes one task, works against a repository, proposes a plan, writes code, runs tests, and opens a pull request. Because Jules has no long-term memory across sessions, the full roadmap is **never** given to it at once — instead, exactly **one phase at a time** is submitted, each fully scoped and self-contained.

Each phase prompt follows a consistent structure: **Objective → Tasks/Sub-tasks → Deliverables → Testing Checklist → Security Checklist → Completion Criteria → Stop Condition.** The Stop Condition is mandatory — it prevents Jules from proceeding into future phases and ensures a human reviews and merges each phase before the next begins.

---

## How to Use This Playbook

1. Copy the **Repo Context Block** below into every new Jules session (it is not persisted automatically).
2. Copy the relevant **phase prompt** immediately after it.
3. Review Jules's proposed plan before it begins substantial work.
4. Before merging any resulting PR, verify it against the **Release-Gate Policy** in [`roadmap.md`](roadmap.md).
5. Only after a phase is merged and verified, move to the next phase prompt.
6. For large phases (e.g. v1.2, v2.0, v5.0), sub-tasks are broken out below and may each be run as a separate Jules session/PR if preferred.
7. With a real repository and issue tracker, it is best practice to create one GitHub issue/milestone per phase and have Jules work against that issue.

---

## Repo Context Block

Paste this at the start of every Jules session, before the phase-specific prompt:

তুমি একটি প্রোডাকশন-গ্রেড AI Assistant প্ল্যাটফর্মের উপর কাজ করছ। এই প্রজেক্টের সামগ্রিক আর্কিটেকচার
"AI-System-Architecture.md" (V1) এবং "AI-System-Architecture-V2-Extension.md" (V2) ডকুমেন্টে সংজ্ঞায়িত,
এবং একটি ভার্সন-বাই-ভার্সন রোডম্যাপ অনুযায়ী বিল্ড হচ্ছে (Foundation → v1.0 → v1.1 → ... → Commercial GA → Enterprise Edition)।

গ্লোবাল নিয়ম (সব ফেজে প্রযোজ্য):

প্রতিটি ভার্সন/ফেজ শেষে সিস্টেম অবশ্যই একটি স্টেবল, ডিপ্লয়যোগ্য, টেস্টেড অবস্থায় থাকতে হবে — আগের কোনো ফিচার ভাঙা যাবে না (regression-safe)।
কাজ শুরুর আগে একটি স্পষ্ট implementation plan লেখো এবং তা অনুসরণ করো। বড় আর্কিটেকচারাল সিদ্ধান্তের আগে থামো ও প্রশ্ন করো।
Stack: ব্যাকএন্ড FastAPI/Go (stateless, containerized), Postgres (মাইগ্রেশন টুল দিয়ে — Alembic/Flyway),
Redis (session/working memory), Qdrant (vector store), NATS/Kafka (event bus), Kubernetes + Helm ডিপ্লয়মেন্ট,
OpenTelemetry + Prometheus + Grafana + Loki (observability), HashiCorp Vault (secrets)। LLM প্রোভাইডার: Anthropic Claude API।
প্রতিটি নতুন ফিচারের জন্য: (a) DB মাইগ্রেশন স্ক্রিপ্ট, (b) API এন্ডপয়েন্ট + OpenAPI স্পেক, (c) ইউনিট টেস্ট (কভারেজ ≥ ৭০%),
(d) ইন্টিগ্রেশন/end-to-end টেস্ট, (e) সিকিউরিটি চেকলিস্ট আইটেম — এই ৫টা ছাড়া কোনো ফিচার "সম্পূর্ণ" ধরা যাবে না।
সিকিউরিটি নন-নেগোশিয়েবল: secret কখনো hardcode/plaintext নয়, সব ইন্টারনাল কমিউনিকেশন mTLS/এনক্রিপ্টেড,
permission/audit log ইমিউটেবল (append-only), least-privilege সব জায়গায়, LLM কনটেক্সটে raw secret কখনো পাস হবে না।
কোড লেখার পর অবশ্যই lint + test + build চালিয়ে যাচাই করবে। যদি existing টেস্ট ভাঙে, রিলিজ-গেট ব্যর্থ হবে — আগে ফিক্স করো।
প্রতিটি ফেজের শেষে একটি "Completion Report" লিখবে: কী implement হলো, কী টেস্ট পাস করলো, কী সিকিউরিটি-আইটেম চেক হলো,
এবং "Completion Criteria" (ওই ফেজের জন্য নির্ধারিত) কীভাবে ডেমো/ভেরিফাই করা যায় তার নির্দেশনা।
তুমি শুধু নিচে দেওয়া ফেজের স্কোপের মধ্যে কাজ করবে। ভবিষ্যতের ফেজের ফিচার আগেভাগে implement করার চেষ্টা করবে না —
তবে ভবিষ্যতে extend করা সহজ হয় এমনভাবে কোড ডিজাইন করবে (interfaces/abstractions রাখো, hardcode এড়াও)।

---

## Phase Prompts

### Phase — Foundation

[Paste Repo Context Block above]

ফেজ: Foundation (Pre-v1.0, Infra Baseline)
লক্ষ্য

পরবর্তী সব ডেভেলপমেন্টের জন্য একটি নিরাপদ, স্বয়ংক্রিয়, পর্যবেক্ষণযোগ্য বেস প্ল্যাটফর্ম প্রতিষ্ঠা করো।
এই ফেজে কোনো ইউজার-ফেসিং ফিচার নেই — pure ইনফ্রাস্ট্রাকচার।

Tasks
Git monorepo স্ক্যাফোল্ড করো (services/, libs/, infra/, docs/ ফোল্ডার স্ট্রাকচার)।
CI/CD পাইপলাইন সেটআপ করো: build → lint → test → security-scan (secret-scanning) → deploy স্টেজ সহ
(GitHub Actions ব্যবহার করো, যেহেতু Jules GitHub-এ চলে)।
একটি dummy "hello world" stateless সার্ভিস তৈরি করো (FastAPI স্কেলেটন) — যাতে CI/CD পাইপলাইন
ভেরিফাই করা যায়।
/healthz এবং /readyz এন্ডপয়েন্ট যোগ করো।
Dockerfile + Helm chart skeleton তৈরি করো dummy সার্ভিসের জন্য।
Postgres মাইগ্রেশন টুলিং (Alembic) সেটআপ করো — খালি স্কিমা দিয়ে শুরু।
Event Bus ক্লায়েন্ট লাইব্রেরি (NATS বা Kafka) তৈরি করো — publish/subscribe wrapper সহ core topic namespace রিজার্ভেশন ডকুমেন্টেড।
Observability বেসলাইন যোগ করো: OpenTelemetry SDK ইন্টিগ্রেশন, Prometheus metrics endpoint, স্ট্রাকচার্ড লগিং (Loki-compatible)।
Secrets management: Vault ইন্টিগ্রেশনের জন্য একটি config-loader abstraction লেখো (env var fallback সহ dev-এর জন্য)।
মাল্টি-এনভায়রনমেন্ট কনফিগ (dev/staging/prod) আলাদা কনফিগ ফাইল/ভ্যালু হিসেবে সেটআপ করো।
CI-তে secret-scanning gate যোগ করো (যেমন gitleaks) যাতে hardcoded secret থাকলে build fail হয়।
Deliverables
Monorepo স্ট্রাকচার + README (কীভাবে লোকালি রান করবে)
CI/CD পাইপলাইন কনফিগ ফাইল
Dummy service + Dockerfile + Helm chart
Event bus client লাইব্রেরি + smoke test
Observability setup ডকুমেন্টেশন
Testing Checklist
 CI পাইপলাইন সফলভাবে build+test+deploy চালাতে পারে (dummy service দিয়ে)
 Event bus publish/subscribe smoke test পাস করে
Security Checklist
 কোনো hardcoded secret নেই (CI gate ভেরিফাইড)
 mTLS/এনক্রিপশন কনফিগারেশন ডকুমেন্টেড (এই ফেজে full enforcement না-ও থাকতে পারে, কিন্তু path/plan থাকতে হবে)
 Least-privilege access নীতি ডকুমেন্টেড
Completion Criteria

একটি "hello world" সার্ভিস কোড-কমিট থেকে CI/CD পাইপলাইনের মধ্য দিয়ে সফলভাবে build+test+deploy হয়,
এবং লগ/মেট্রিক observability স্ট্যাকে দেখা যায়।

Stop Condition

উপরের সব Deliverable + Testing Checklist সম্পন্ন হলে একটি PR খোলো, Completion Report লেখো, এবং থামো।
পরবর্তী ফেজ (v1.0 MVP) শুরু করো না।


### Phase — v1.0 MVP (Conversational Core)

[Paste Repo Context Block above]

পূর্বশর্ত

Foundation ফেজ merge হয়ে গেছে ধরে নাও। এই ফেজ তার উপর বিল্ড করবে।

ফেজ: v1.0 MVP — Conversational Core
লক্ষ্য

একটি single-agent, টেক্সট-বেসড কনভারসেশনাল অ্যাসিস্ট্যান্ট তৈরি করো যেখানে বেসিক মেমোরি ও
coarse-grained permission আছে — end-to-end পাইপলাইন প্রমাণ করা এই ফেজের মূল কাজ।

Sub-tasks (প্রতিটি আলাদা PR হিসেবেও করা যায়)
1.0.a — Auth & Identity
users, tenants, sessions টেবিল + মাইগ্রেশন
POST /v1/auth/login, POST /v1/auth/refresh — JWT ভিত্তিক, bcrypt/argon2 পাসওয়ার্ড হ্যাশিং
Refresh-token rotation লজিক
1.0.b — Conversational Agent Service
একক LLM (Anthropic Claude API) ইন্টিগ্রেশন — retry/timeout handling সহ
POST /v1/conversations, POST /v1/conversations/{id}/messages, GET /v1/conversations/{id}/history
Redis-ভিত্তিক Working Memory (সেশন-স্কোপড কনটেক্সট)
1.0.c — Semantic Memory
memory_semantic টেবিল + Qdrant vector collection (semantic_memory)
বেসিক RAG: প্রতিটি নতুন মেসেজে top-k রিলেভেন্ট ফ্যাক্ট রিট্রিভ করে system prompt-এ inject করা
DELETE/right-to-forget সাপোর্ট এই টেবিলের জন্য
1.0.d — Tooling: Web Search
Tool SDK v1 (manifest-based ইন্টারফেস, ভবিষ্যতের প্লাগইনের জন্য extensible রাখো)
একটি Web Search টুল ইমপ্লিমেন্ট করো (কোনো একটা search API ব্যবহার করে) — API down হলে graceful fallback
1.0.e — Permission Engine (Coarse-grained)
permissions, permission_audit_log টেবিল (audit log অবশ্যই append-only/immutable)
POST /v1/permissions/grant, POST /v1/permissions/revoke
প্রতিটি টুল-কলের আগে allow/deny চেক
1.0.f — Task Management Engine
tasks টেবিল, স্টেট মেশিন (queued → running → completed/failed)
GET /v1/tasks/{id}
Event topics: task.created/updated/completed
1.0.g — Minimal Web UI
লগইন পেজ, চ্যাট উইন্ডো, বেসিক সেটিংস পেজ
টুল-কলের আগে permission-grant confirmation modal
Desktop-first, রেসপন্সিভ ডিজাইন বাধ্যতামূলক নয়
Testing Checklist
 Unit test coverage ≥ ৭০% কোর সার্ভিসে
 End-to-end টেস্ট: signup → message পাঠানো → response পাওয়া → পরের সেশনে memory persist হওয়া
 Load test: ১০০ concurrent সেশনে latency বেঞ্চমার্ক
 Web-search টুল ফেইলিওর-কেস হ্যান্ডলিং টেস্ট
Security Checklist
 পাসওয়ার্ড কখনো plaintext স্টোর হয় না
 JWT এক্সপায়ারি + রিফ্রেশ-টোকেন রোটেশন কার্যকর
 SQL injection/XSS বেসিক স্ক্যান (OWASP ZAP বা সমতুল্য)
 Permission audit log immutable ভেরিফাইড
 Right-to-forget এন্ডপয়েন্ট কাজ করে
Completion Criteria

একজন real ইউজার সাইন-আপ করে, একটি ওয়েব-সার্চ-প্রয়োজনীয় প্রশ্ন করে, সঠিক উত্তর পায়, এবং পরের সেশনে
সিস্টেম আগের প্রাসঙ্গিক তথ্য মনে রাখে — সবকিছু permission-gated ও audited।

Stop Condition

সব sub-task + checklist সম্পন্ন হলে PR(s) খোলো, Completion Report লেখো, এবং থামো। v1.1 শুরু করো না।


### Phase — v1.1 Voice Pipeline

[Paste Repo Context Block above]

পূর্বশর্ত

v1.0 MVP merge ও verify হয়ে গেছে।

ফেজ: v1.1 — Voice Pipeline
লক্ষ্য

টেক্সট-চ্যাটে প্রমাণিত কোরের উপর ভয়েস ইন্টারঅ্যাকশন যোগ করো।

Sub-tasks
1.1.a — Streaming Infra
WS /ws/voice-stream দ্বিমুখী অডিও স্ট্রিমিং এন্ডপয়েন্ট
Voice Streaming Gateway (WebRTC/WebSocket), Opus/PCM কোডেক হ্যান্ডলিং
voice_sessions টেবিল, sessions.input_modality কলাম যোগ
1.1.b — STT/TTS
VAD সার্ভিস + স্ট্রিমিং STT (Whisper, বাংলা+ইংরেজি কোড-মিক্স সাপোর্ট সহ)
স্ট্রিমিং TTS (কমপক্ষে ১টা বাংলা + ১টা ইংরেজি ভয়েস)
Barge-in সাপোর্ট (মাঝপথে ইন্টারাপ্ট করা)
1.1.c — Wake-word + Speaker ID
লোকাল wake-word ডিটেকশন মডিউল
Speaker identification (multi-user device কনটেক্সট, per-tenant isolated)
Offline fallback mode (lightweight local model)
1.1.d — UI
Push-to-talk/always-listening টগল
রিয়েল-টাইম ট্রান্সক্রিপশন ডিসপ্লে + অডিও ওয়েভফর্ম ইন্ডিকেটর
GET /v1/voice/devices
Testing Checklist
 STT accuracy বেঞ্চমার্ক (WER) বাংলা+ইংরেজি স্যাম্পলে
 Barge-in ফাংশনাল টেস্ট
 নেটওয়ার্ক-ড্রপ সিমুলেশনে offline fallback ট্রিগার হয়
 মাল্টি-স্পিকার শনাক্তকরণ নির্ভুলতা টেস্ট
Security Checklist
 Raw অডিও permanent store হয় না (শুধু transcribed text, explicit opt-in ছাড়া)
 Voice stream এনক্রিপ্টেড (DTLS-SRTP/WSS)
 Speaker-identification ডেটা per-tenant isolated
Completion Criteria

ইউজার ভয়েসে প্রশ্ন করে, রিয়েল-টাইমে transcribe হয়, LLM response ভয়েসে ফিরে আসে, এবং
কথার মাঝে থামিয়ে নতুন কমান্ড দেওয়া যায়।

Stop Condition

সব সম্পন্ন হলে PR + Completion Report, তারপর থামো। v1.2 শুরু করো না।


### Phase — v1.2 Multi-Agent Core + Tool/Plugin Framework

[Paste Repo Context Block above]

পূর্বশর্ত

v1.0 এবং v1.1 merge হয়ে গেছে।

ফেজ: v1.2 — Multi-Agent Core + Tool/Plugin Framework
লক্ষ্য

সিঙ্গেল-এজেন্ট থেকে Orchestrator-Worker মাল্টি-এজেন্ট আর্কিটেকচারে উত্তরণ এবং একটি
MCP-compatible, sandboxed টুল/প্লাগইন ফ্রেমওয়ার্ক প্রতিষ্ঠা করো।

Sub-tasks
1.2.a — Orchestrator + Agent Registry
Orchestrator Service (routing + planning, intent → task-plan DAG কম্পাইলেশন)
Agent Capability Registry (agents_registry টেবিল)
gRPC internal service-to-service communication
1.2.b — Specialist Agents
Coder Agent, Researcher Agent (২টা স্পেশালিস্ট এজেন্ট)
Blackboard-pattern এজেন্ট কমিউনিকেশন
1.2.c — Plugin Runtime
Plugin/Tool SDK v1: manifest-based, sandboxed execution (WASM বা gVisor)
plugins_registry, installed_plugins টেবিল
GET /v1/plugins/marketplace, POST /v1/plugins/{id}/install, DELETE /v1/plugins/{id}/uninstall
প্রতি-প্লাগইন রিসোর্স-লিমিট এনফোর্সমেন্ট
1.2.d — UI
"কোন এজেন্ট কাজ করছে" transparency indicator
Plugin install/manage পেজ
Testing Checklist
 মাল্টি-এজেন্ট টাস্ক (Coder+Researcher একসাথে) end-to-end টেস্ট
 Plugin sandbox escape penetration test
 এজেন্ট ফেইলিওর → retry/fallback লজিক টেস্ট
 একটি প্লাগইন ক্র্যাশ করলে বাকি সিস্টেম unaffected থাকে (isolation টেস্ট)
Security Checklist
 Plugin manifest-ঘোষিত permission-এর বাইরে কোনো action ব্লক হয় (ভেরিফাইড)
 Sandbox থেকে host-level access সম্পূর্ণ বন্ধ (pen-test ভেরিফাইড)
 Third-party প্লাগইন code-signing verification কার্যকর
Completion Criteria

একটি জটিল রিকোয়েস্ট (যেমন "এই কোড রিসার্চ করে বাগ ফিক্স করো") Orchestrator দুইটা এজেন্টে ভাগ করে,
উভয়ে সমন্বিতভাবে একটি সঠিক সমাধান দেয়।

Stop Condition

সব সম্পন্ন হলে PR + Completion Report, তারপর থামো। v2.0 শুরু করো না।


### Phase — v2.0 Computer Control + Permission Hardening + Security

[Paste Repo Context Block above]

পূর্বশর্ত

v1.2 (Multi-agent architecture) merge হয়ে গেছে — এটি কঠোর প্রিরিকুইজিট।

ফেজ: v2.0 — Computer Control + Permission Hardening + Security
লক্ষ্য

সিস্টেমকে ইউজারের কম্পিউটারে নিরাপদে অ্যাকশন নিতে সক্ষম করো, এবং একটি ফুল-গ্রেড
গ্র্যানুলার permission/security স্ট্যাক প্রতিষ্ঠা করো।

Sub-tasks
2.0.a — Computer Control Levels
L1 (read-only) → L2 (app interaction) → L3 (file operations)
OS-native Accessibility API ইন্টিগ্রেশন (Windows/macOS/Linux)
Vision-model fallback (accessibility API না থাকা legacy app-এর জন্য screenshot-based action)
2.0.b — Execution Broker + Rollback
Execution Broker সম্পূর্ণ আলাদা process (মূল এজেন্ট প্রসেসের কখনো direct root/admin access নয়)
execution_snapshots টেবিল, dry-run mode, rollback/undo log
POST /v1/computer-control/execute (dry-run flag সহ), POST /v1/computer-control/rollback/{execution_id}
2.0.c — Permission Engine v2 (RBAC + ABAC)
permissions টেবিল extend (risk_level, attribute-based কলাম)
Just-in-time confirmation UX (ঝুঁকি-লেভেল অনুযায়ী toast vs modal vs biometric-confirm)
2.0.d — Guardian Agent + Anomaly Detection
Guardian Agent (পলিসি এনফোর্সমেন্ট)
anomaly_detection_log, GET /v1/security/anomalies
Agent trust-score ভিত্তিক ডাইনামিক রাউটিং
2.0.e — UI
Dry-run preview screen ("এটা করলে কী হবে")
Permission management dashboard (grant/revoke history)
Testing Checklist
 L1-L3 প্রতিটি capability level আলাদা functional test
 Rollback মেকানিজম টেস্ট
 Permission-denied path টেস্ট
 Anomaly detection true-positive/false-positive rate বেঞ্চমার্ক
Security Checklist
 পূর্ণাঙ্গ penetration test (সম্ভব হলে external firm দিয়ে)
 Execution Broker privilege-escalation test
 Audit log completeness verification
 Secrets কখনো LLM context-এ সরাসরি পাস হয় না (tool broker layer verified)
 Prompt-injection defense test (malicious web-content দিয়ে)
Completion Criteria

ইউজার ভয়েসে বলে "এই ফোল্ডারের পুরনো ফাইল মুছে দাও" — সিস্টেম dry-run preview দেখায়, confirmation নেয়,
execute করে, এবং rollback সম্ভব — পুরো প্রসেস audit-logged।

Stop Condition

সব সম্পন্ন হলে PR + Completion Report, তারপর থামো। v2.1 শুরু করো না।


### Phase — v2.1 Emotion Detection + Automation Engine

[Paste Repo Context Block above]

পূর্বশর্ত

v1.1 (Voice) এবং v1.2 (Agent) merge হয়ে গেছে। (v2.0-এর সাথে প্যারালালে করা সম্ভব, কিন্তু
এই প্রম্পট ধরে নিচ্ছে v2.0-ও merge হয়ে গেছে যদি sequential করেন।)

ফেজ: v2.1 — Emotion Detection + Automation Engine
লক্ষ্য

আবেগ-সংবেদনশীল response এবং ইউজার-সংজ্ঞায়িত automation রুল সাপোর্ট যোগ করো।

Sub-tasks
2.1.a — Emotion Detection
মাল্টি-মোডাল emotion detection সার্ভিস (voice prosody + text sentiment), valence/arousal আউটপুট
memory_semantic-এ emotion_tag কলাম, session-scoped by default (দীর্ঘমেয়াদি প্রোফাইলিং শুধু opt-in)
Prosody-adaptive TTS প্যারামিটার ম্যাপিং
2.1.b — Automation Engine
automation_rules, automation_execution_log টেবিল
Trigger→Condition→Action রুল ইঞ্জিন, event-bus subscription ভিত্তিক ট্রিগার + cron scheduler
Conversational rule-builder ("প্রতিদিন সকাল ৮টায়...") → automation compiler
Safe-mode/dry-run automation execution
2.1.c — UI
Automation রুল list/editor (visual বা conversational)
Conflict-warning UI
Testing Checklist
 Emotion detection accuracy বেঞ্চমার্ক (labeled test set)
 Automation রুল conflict-detection টেস্ট
 Safe-mode → full-auto transition টেস্ট
Security Checklist
 Automation রুল permission bypass করতে পারে না (পুরো permission chain পাস করে verified)
 Emotion data default session-scoped
Completion Criteria

ইউজার frustration দেখালে সিস্টেম টোন বদলায়; ইউজার একটি ভয়েস-কমান্ডে automation রুল তৈরি করে,
এবং সেটা নির্ধারিত সময়ে নিরাপদে execute হয়।

Stop Condition

সব সম্পন্ন হলে PR + Completion Report, তারপর থামো। v3.0 শুরু করো না।


### Phase — v3.0 Learning System + Memory Maturity (V1 GA)

[Paste Repo Context Block above]

পূর্বশর্ত

v2.0 এবং v2.1 merge হয়ে গেছে।

ফেজ: v3.0 — Learning System + Memory Maturity (V1 আর্কিটেকচার সম্পূর্ণ / Internal Beta)
লক্ষ্য

Episodic/Procedural memory, feedback capture, এবং preference personalization যোগ করে
V1 রোডম্যাপ সম্পূর্ণ করো।

Sub-tasks
3.0.a — Episodic/Procedural Memory
episodic_memory, procedural_memory vector collection
Memory Consolidation Job (periodic, off-peak batch scheduler)
Forgetting curve/importance scoring মডেল (recency+frequency+emotional-salience)
3.0.b — Feedback + Preference
feedback_events টেবিল, implicit+explicit feedback capture
Thumbs up/down UI প্রতিটি response-এ
Preference-vector personalization (static)
GET /v1/memory?type=..., DELETE /v1/memory/{id}, Memory browser/editor UI
Testing Checklist
 Memory consolidation job idempotency টেস্ট
 Forgetting-curve decay logic verification
 Preference-vector আপডেট সঠিকভাবে conversation-এ প্রতিফলিত হয়
Security Checklist
 Right-to-forget সম্পূর্ণ কার্যকর (episodic+procedural মেমোরিতেও)
 Per-user data isolation verified (cross-user leak টেস্ট)
Completion Criteria

V1 আর্কিটেকচার সম্পূর্ণভাবে implemented — সিস্টেম একটি functional, secure, personal AI assistant
হিসেবে internal beta/soft-launch-যোগ্য।

Stop Condition

সব সম্পন্ন হলে PR + Completion Report। এটি একটি বড় মাইলস্টোন — এখানে থামো এবং পুরো V1 এর
regression suite (Foundation থেকে v3.0 পর্যন্ত সব completion criteria) চালিয়ে রিপোর্ট করো,
তারপর মানবিক রিভিউর জন্য অপেক্ষা করো। v3.1 শুরু করো না।


### Phase — v3.1 AI-OS Core

[Paste Repo Context Block above]

পূর্বশর্ত

v3.0 (V1 GA) সম্পূর্ণ ও stable। এটি কঠোর প্রিরিকুইজিট — এই ফেজ V1-কে "wrap" করবে,
তাই V1 অবশ্যই স্টেবল থাকতে হবে।

ফেজ: v3.1 — AI-OS Core
লক্ষ্য

একটি কেন্দ্রীয় "কার্নেল" লেয়ার প্রতিষ্ঠা করো যা ভবিষ্যতের সব capability-growth কোর-কোড-পরিবর্তন
ছাড়াই সম্ভব করবে। এটি একটি architectural মাইলস্টোন, নতুন ইউজার-ফিচার নয় — কোনো ইউজার-দৃশ্যমান
পরিবর্তন/ডাউনটাইম হওয়া উচিত না।

Sub-tasks
3.1.a — Capability Registry
capability_registry টেবিল, capability_embeddings vector collection
Embedding-based semantic capability matching (ANN index)
GET /v2/ai-os/capabilities, POST /v2/ai-os/capabilities/register
Signed manifest verification (malicious/spoofed entry প্রতিরোধ)
3.1.b — Context Manager + Governance Router
Context Manager (workspace/mood/session কেন্দ্রীয় ট্র্যাকিং), GET /v2/ai-os/context
Governance Router — permission+policy unified check, কখনো bypass করা যাবে না এমনভাবে ডিজাইন করো
(প্রতিটি dispatch path এই router দিয়ে যেতে বাধ্য)
3.1.c — Central Dispatch + Backward Compatibility
v1.2 Orchestrator-কে Central Dispatch-এর "planning module" হিসেবে wrap করো (backward-compatible)
Feature-flag ইনফ্রাস্ট্রাকচার (V2 রোলআউটের জন্য)
একটি সম্পূর্ণ backward-compatibility রিগ্রেশন suite লেখো: v1.0 থেকে v3.0 পর্যন্ত সব existing
API/flow AI-OS Core চালুর পরেও অপরিবর্তিতভাবে কাজ করে কিনা যাচাই করো
Testing Checklist
 রিগ্রেশন suite: V1-এর সব ফিচার AI-OS Core চালুর পরেও অপরিবর্তিতভাবে পাস করে
 Capability registration → discovery latency বেঞ্চমার্ক
 Feature-flag toggle/rollback টেস্ট
Security Checklist
 Governance Router কখনো bypass করা যায় না (কোনো dispatch path permission-check এড়াতে পারে না — verified)
 Capability Registry-তে malicious/spoofed entry registration প্রতিরোধ (signed manifest verified)
Completion Criteria

V1-এর প্রতিটি existing ফিচার AI-OS Core-এর মধ্য দিয়ে রাউট হচ্ছে, কোনো ব্যবহারকারী-দৃশ্যমান
পরিবর্তন/ডাউনটাইম ছাড়াই — এবং একটি dummy test capability রেজিস্টার করে দেখানো যায় যে এটি
কোড-ডিপ্লয় ছাড়াই discoverable।

Stop Condition

সব সম্পন্ন হলে PR + Completion Report, তারপর থামো। v4.0 শুরু করো না।


### Phase — v4.0 Skill Framework + Project Workspace

[Paste Repo Context Block above]

পূর্বশর্ত

v3.1 AI-OS Core merge হয়ে গেছে।

ফেজ: v4.0 — Skill Framework + Project Workspace
লক্ষ্য

পুনঃব্যবহারযোগ্য "স্কিল" ধারণা ও দীর্ঘমেয়াদি প্রজেক্ট কনটেইনার চালু করো।

Sub-tasks
4.0.a — Skill Registry + Executor
skills_registry, installed_skills, skill_execution_log টেবিল, skill_embeddings vector collection
Skill Manifest ফরম্যাট নির্ধারণ করো, Skill Executor (AI-OS Core dispatch-এর সাথে ইন্টিগ্রেটেড)
৫টা সিস্টেম-প্রোভাইডেড স্কিল implement করো (যেমন Meeting Summarizer, Report Generator, Email Drafter,
Data Extractor, Task Planner)
GET /v2/skills, POST /v2/skills/{id}/install, POST /v2/skills/{id}/invoke
Trigger-phrase → skill matching (semantic + capability registry)
4.0.b — Skill Authoring
Conversational skill-teaching ফ্লো — ইউজার কথোপকথনে নতুন স্কিল "শেখাতে" পারবে
POST /v2/skills/author
Skill install-এ granular permission confirmation (bundle-grant নয়)
4.0.c — Project Workspace
workspaces টেবিল, Project Workspace Service (দীর্ঘমেয়াদি কনটেইনার, scoped memory)
Workspace-scoped memory namespace isolation
POST /v2/workspaces, GET /v2/workspaces/{id}, GET /v2/workspaces/{id}/dashboard
Workspace Dashboard UI (progress, timeline, linked task/file view)
Testing Checklist
 প্রতিটি সিস্টেম-স্কিল functional test (কমপক্ষে ৫টা কোর স্কিল)
 Workspace memory-isolation টেস্ট (cross-workspace leak না হওয়া verified)
 User-authored skill compilation end-to-end টেস্ট
Security Checklist
 Skill ইনস্টলে granular permission confirmation verified
 Workspace collaborator permission scope সঠিকভাবে enforced
Completion Criteria

ইউজার একটি Workspace তৈরি করে, একটি সিস্টেম-স্কিল invoke করে সফল result পায়, এবং conversationally
একটি নতুন কাস্টম স্কিল "শেখায়" যা পরবর্তীতে পুনরায় ব্যবহারযোগ্য।

Stop Condition

সব সম্পন্ন হলে PR + Completion Report, তারপর থামো। v4.1 শুরু করো না।


### Phase — v4.1 Personality Engine

[Paste Repo Context Block above]

পূর্বশর্ত

v3.1 AI-OS Core merge হয়ে গেছে (v4.0-এর সাথে প্যারালালেও করা যায়)।

ফেজ: v4.1 — Personality Engine
লক্ষ্য

সামঞ্জস্যপূর্ণ, customizable সিস্টেম-ব্যক্তিত্ব চালু করো।

Sub-tasks
personality_profiles টেবিল
Base Persona নির্বাচন (onboarding flow), tone parameters (formality, warmth, humor, verbosity)
Adaptive tone layer (emotion-signal ভিত্তিক সাময়িক modulation — v2.1 emotion detection ব্যবহার করে)
Per-workspace persona override
Consistency Guard middleware — সব output-generating path-এ (এজেন্ট/স্কিল নির্বিশেষে) inject করো
Tone-parameter → prompt-modifier mapping logic
Safety-priority enforcement: persona কখনো safety/honesty নীতি override করতে পারবে না
GET /v2/personality/profile, PATCH /v2/personality/profile
UI: Persona configuration screen (slider/preset) + preview ("এই সেটিং দিয়ে সিস্টেম কেমন উত্তর দেবে")
Testing Checklist
 বিভিন্ন এজেন্ট/স্কিলজুড়ে persona-consistency টেস্ট
 Emotion-adaptive tone-shift টেস্ট (স্থায়ী প্রোফাইল না বদলে সাময়িক modulation)
 Safety-override টেস্ট (persona যেন কখনো harmful/dishonest output অনুমতি না দেয়)
Security Checklist
 Personality Engine কোনোভাবে V1 Security Model/Permission Engine bypass করতে পারে না (verified)
Completion Criteria

ইউজার persona কনফিগার করে, এবং বিভিন্ন এজেন্ট/স্কিল থেকে আসা সব response-এ সামঞ্জস্যপূর্ণ টোন
প্রতিফলিত হয়, emotional context অনুযায়ী সাময়িক adjust হলেও কোর ব্যক্তিত্ব অটুট থাকে।

Stop Condition

সব সম্পন্ন হলে PR + Completion Report, তারপর থামো। v5.0 শুরু করো না।


### Phase — v5.0 Long-Term Learning + Multi-Agent Collaboration + Daily Assistant

[Paste Repo Context Block above]

পূর্বশর্ত

v4.0 (Skill/Workspace ডেটা প্রয়োজন) merge হয়ে গেছে। নোট: এই ফেজে যথেষ্ট real-usage ডেটা
প্রয়োজন — যদি এখনো পর্যাপ্ত real usage না থাকে, Jules-কে সিন্থেটিক/সিমুলেটেড ডেটাসেট দিয়ে
টেস্ট করতে বলো এবং প্রোডাকশন rollout-এর আগে সতর্ক করতে বলো।

ফেজ: v5.0 — Long-term Learning + Multi-Agent Collaboration + Daily Assistant
লক্ষ্য

গভীরতর দীর্ঘমেয়াদি বুদ্ধিমত্তা, পরিশীলিত এজেন্ট-সহযোগিতা, এবং proactivity যোগ করো।

Sub-tasks (৩টা বড় গ্রুপ — আলাদাভাবে সিকোয়েন্স করা যায়)
গ্রুপ ১ — Long-term Learning
Skill Refinement Loop (offline batch analysis)
Cross-workspace Pattern Mining (privacy-preserving, per-user isolated)
Longitudinal Preference Drift Tracking (versioned)
agents_registry.trust_score-কে continuous recalculation-এ যুক্ত করা (Agent Performance Trust Scoring)
গ্রুপ ২ — Multi-Agent Collaboration
agent_negotiation_log টেবিল, Structured Negotiation Message protocol (proposal/counter-proposal/accept-reject)
Peer Review/Cross-check প্যাটার্ন
Debate/Consensus প্যাটার্ন (উচ্চ-ঝুঁকির সিদ্ধান্তে)
Conflict Resolution Agent, Sub-team Formation (ডাইনামিক)
Explainability generation (মানুষ-পঠনযোগ্য কারণ)
GET /v2/collaboration/{task_id}/trace, Collaboration trace viewer UI
গ্রুপ ৩ — Daily Assistant
daily_briefing_log টেবিল, Daily Briefing Generator (batch, off-peak)
Contextual Nudges, Routine Detection & Suggestion, End-of-day wind-down (ঐচ্ছিক)
GET /v2/daily-assistant/briefing, PATCH /v2/daily-assistant/preferences
UI: Daily Briefing card/notification, Explainability tooltip ("কেন এই সাজেশন")
Testing Checklist
 Peer-review প্যাটার্ন end-to-end টেস্ট
 Consensus/escalation logic টেস্ট (দ্বিমত হলে human-escalation ট্রিগার হয় কিনা)
 Daily Briefing accuracy/relevance টেস্ট
 Trust-score recalculation correctness টেস্ট
Security Checklist
 Delegation ≠ automatic trust — প্রতিটি agent-to-agent delegation-এ পুনরায় permission-check verified
 Cross-workspace pattern mining কখনো cross-user ডেটা লিক করে না (isolation টেস্ট)
 Learning সিগন্যাল explainable ও ইউজার-রিসেটযোগ্য
Completion Criteria

একটি উচ্চ-ঝুঁকির/অস্পষ্ট সিদ্ধান্তে একাধিক এজেন্ট বিতর্ক করে consensus-এ পৌঁছায় (বা human-escalate করে);
প্রতিদিন সকালে ইউজার একটি প্রাসঙ্গিক briefing পায়; সিস্টেম repetitive প্যাটার্ন শনাক্ত করে নতুন
automation/skill সাজেস্ট করে।

Stop Condition

সব সম্পন্ন হলে PR + Completion Report, তারপর থামো। v5.1 শুরু করো না।


### Phase — v5.1 Governance Layer

[Paste Repo Context Block above]

পূর্বশর্ত

v4.0, v5.0-এর যথেষ্ট অংশ merge হয়ে গেছে (অর্থবহ policy বানাতে পর্যাপ্ত real-usage ডেটা প্রয়োজন)।

ফেজ: v5.1 — Governance Layer
লক্ষ্য

প্রাতিষ্ঠানিক নীতি, কমপ্লায়েন্স, এবং ফরমাল human-review workflow প্রতিষ্ঠা করো —
commercial/enterprise readiness-এর পূর্বশর্ত।

Sub-tasks
governance_policies, compliance_audit_log টেবিল
Policy Engine (org-level রুল সংজ্ঞা/এনফোর্সমেন্ট) — v3.1 Governance Router-এর সাথে synchronous
check integration (কখনো একটিকে bypass করে অন্যটি দিয়ে পাস করা যাবে না)
Compliance Module (data residency, retention নীতি)
Explainability Service (decision → human-readable rationale)
Governance Audit Council workflow service (human-review escalation)
Cost/Resource Governance (quota, budget-alert)
GET/POST /v2/governance/policies, GET /v2/governance/audit-log, GET /v2/governance/explain/{decision_id}
UI: Governance/Compliance dashboard, Policy rule-builder, Cost/quota monitoring dashboard
Testing Checklist
 Policy violation detection টেস্ট (নিয়ম ভাঙার চেষ্টা ব্লক হয় কিনা)
 Audit Council escalation workflow end-to-end টেস্ট
 Cost quota breach → alert trigger টেস্ট
Security Checklist
 Policy Engine + Permission Engine (V1) — কোনো path একটিকে এড়িয়ে অন্যটি দিয়ে পাস করতে পারে না
 Compliance audit log tamper-proof (WORM storage verified)
 Explainability output-এ sensitive ডেটা লিক হয় না (verified)
Completion Criteria

একজন compliance-officer একটি org-level policy সেট করে (যেমন "L4 command শুধু admin"), সিস্টেম
স্বয়ংক্রিয়ভাবে তা enforce করে, এবং যেকোনো সিদ্ধান্তের জন্য human-readable ব্যাখ্যা পাওয়া যায়।

Stop Condition

সব সম্পন্ন হলে PR + Completion Report, তারপর থামো। Commercial GA শুরু করো না।


### Phase — Commercial Release (GA)

[Paste Repo Context Block above]

পূর্বশর্ত

v5.1 Governance সম্পূর্ণ ও stable — এটি কঠোর প্রিরিকুইজিট।

ফেজ: Commercial Release (General Availability)
লক্ষ্য

প্রোডাক্টকে পাবলিকলি বিক্রয়যোগ্য, SLA-backed, multi-tenant commercial সার্ভিসে রূপান্তর করো।

Sub-tasks
GA.a — Multi-tenancy Hardening
পূর্ণ tenant isolation audit (আগের সব ফিচারজুড়ে)
GA.b — Billing
billing_usage টেবিল, usage-based metering
Payment gateway integration, GET /v1/billing/usage, POST /v1/billing/subscribe
Billing/Subscription management UI
GA.c — Marketplace
plugins_registry/skills_registry-তে pricing/revenue-share কলাম
Marketplace Revenue-share Engine, publisher portal UI
GA.d — Team Collaboration + SLA + Multi-region
Workspace Team Collaboration (পূর্ণ role-based)
SLA monitoring + public status page
Multi-region deployment infra (data-residency compliance), load-balancer + auto-scaling
পূর্ণাঙ্গ প্রোডাকশন কনফিগারেশন
Testing Checklist
 ফুল-স্কেল load test (expected peak ট্রাফিকের ২-৩x)
 Chaos engineering টেস্ট (node failure, network partition simulation)
 Multi-tenant isolation penetration test (cross-tenant data access চেষ্টা)
 Billing accuracy reconciliation test
Security Checklist
 থার্ড-পার্টি সিকিউরিটি অডিট (external firm) সম্পন্ন ও critical finding resolved
 SOC2/ISO27001-স্টাইল কমপ্লায়েন্স চেকলিস্ট রিভিউ (যদি target market প্রয়োজন করে)
 Disaster Recovery drill সম্পন্ন (RTO/RPO টার্গেট verified)
 Payment ডেটা PCI-DSS scope compliance (অথবা PCI-compliant gateway ব্যবহার)
Completion Criteria

পাবলিক সাইন-আপ ওপেন, প্রথম paying customer সফলভাবে subscribe করে, ব্যবহার করে, বিল পায় —
সবকিছু প্রকাশিত SLA-এর মধ্যে, এবং একটি স্বাধীন সিকিউরিটি অডিট পাস করা হয়েছে।

Stop Condition

সব সম্পন্ন হলে PR + Completion Report, তারপর থামো। Enterprise Edition শুরু করো না
(এটি ঐচ্ছিক এবং GA স্টেবল হওয়ার পরই বিবেচনা করা উচিত)।


### Phase — Enterprise Edition (Optional)

[Paste Repo Context Block above]

পূর্বশর্ত

Commercial GA stable — এটি কঠোর প্রিরিকুইজিট।

ফেজ: Enterprise Edition
লক্ষ্য

বড় প্রতিষ্ঠানের জন্য উচ্চ-নিয়ন্ত্রণ, self-hostable, deeply-compliant সংস্করণ সরবরাহ করো।

Sub-tasks
On-premise/private-cloud deployment (Helm chart-based, self-host), air-gapped সাপোর্ট
(প্রয়োজনে LLM local-inference fallback বিবেচনাসহ)
SSO/SAML/OIDC enterprise IdP integration connector
Governance Policy Packs (industry-specific compliance bundle — healthcare/finance)
Dedicated Governance-as-a-Service instance provisioning
White-label/custom domain agent সাপোর্ট
Advanced audit/compliance reporting (exportable — PDF/CSV)
Custom SLA + dedicated support channel ডকুমেন্টেশন
tenants টেবিল extend (deployment_mode, sso_config), policy_pack_installations টেবিল
POST /v2/enterprise/sso/configure, POST /v2/enterprise/policy-packs/install,
GET /v2/enterprise/compliance-report/export
UI: Enterprise Admin Console (SSO config, policy-pack management, user provisioning),
Compliance report export UI
Testing Checklist
 On-prem deployment end-to-end installation test (ডকুমেন্টেড স্টেপ অনুসরণ করে install করা যায় কিনা)
 SSO integration test (একাধিক IdP-এর বিরুদ্ধে)
 Policy pack conflict/override test
Security Checklist
 Air-gapped deployment-এ কোনো unintended external network call নেই (verified)
 Enterprise-grade encryption-key management (customer-managed keys অপশন)
 প্রতিটি বড় enterprise deployment-এর আগে dedicated penetration test
Completion Criteria

একটি enterprise client নিজস্ব ইনফ্রাস্ট্রাকচারে সফলভাবে সিস্টেম deploy করে, নিজেদের SSO দিয়ে
login করে, একটি industry-নির্দিষ্ট compliance-pack চালু করে, এবং একটি audit report export করে।

Stop Condition

সব সম্পন্ন হলে PR + Completion Report, তারপর থামো। প্রজেক্ট রোডম্যাপ সম্পূর্ণ।


---

## Release-Gate Reference

Every PR must satisfy the **Release-Gate Policy** defined canonically in [`roadmap.md`](roadmap.md) before merging: all testing checklist items pass, all security checklist items pass with no open critical/high findings, completion criteria are demonstrated, and all prior versions' completion criteria still hold.

---

## Parallelization Reference

See the **Dependency & Parallelization Matrix** in [`roadmap.md`](roadmap.md) for which phases can be run as separate, simultaneous Jules sessions (e.g. v1.1 + v1.2, v2.0 + v2.1, v4.0 + v4.1).

---

## Quick-Start Checklist

1. [ ] Create a GitHub repository and connect it to Google Jules
2. [ ] Submit the "Foundation" phase prompt to Jules
3. [ ] Review and approve Jules's plan
4. [ ] Verify the release-gate checklist before merging the PR
5. [ ] Move to the next phase — paste the Repo Context Block plus the next phase prompt in a new session
6. [ ] Every 3–4 phases, run a full regression pass verifying all prior completion criteria still hold