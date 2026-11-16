---
section: governance
status: published
locale: en-US
date: 2026-11-16
---
# Governance & Openness — Ten Decisions That Shaped This Project

> This guide doesn't rewrite the ADRs — the full originals are linked throughout. What it tells is the story arc: ten architecture decisions made between 2026-10-25 and 2026-11-15, and how they shaped the project you are looking at. It closes with the openness policy itself (ADR-010): why a banking-system project dares to lay its entire process open.

## Act One: Standing on Shoulders (2026-10-25 — four calls in a row)

Day one settled how the foundation gets built:

1. **[ADR-001: don't rewrite Fineract](../../../planning/abnk-design/adr/zh-CN/001-no-rewrite.md)** — the core ledger reuses Apache Fineract as-is (7,100 Java files, 473 Liquibase changelogs, 200 E2E scenarios — a battle-tested engine). Differentiation goes to localization, channel experience, integrations, and data intelligence;
2. **[ADR-002: all customization in `custom/abnk/` modules](../../../planning/abnk-design/adr/zh-CN/002-custom-modules.md)** — "don't rewrite" doesn't mean "don't customize": every line of custom code lives in physically isolated module paths, keeping the fork quarter-level mergeable with upstream. The "never touch the core" rule has exactly one single-line exception, precise enough to be written into the ADR itself;
3. **[ADR-003: PostgreSQL as the single database host](../../../planning/abnk-design/adr/zh-CN/003-postgresql-baseline.md)** — follow upstream's standardization; credentials aligned across three layers so local debugging runs with zero environment overrides;
4. **[ADR-004: Fineract's native multi-tenancy, phased in](../../../planning/abnk-design/adr/zh-CN/004-multi-tenancy.md)** — the architecture is free and physically isolated per-tenant databases naturally satisfy financial data-compliance; but it rolls out in stages, not before there is business data to validate it with.

The shared logic: **high-complexity, low-differentiation infrastructure comes from mature open source; in-house effort goes only where it differentiates.**

## Act Two: Channel and Product Boundaries (same day, two more)

5. **[ADR-005: three self-built frontends](../../../planning/abnk-design/adr/zh-CN/005-frontend-strategy.md)** — back office, teller, and online/mobile banking get separate frontends built to their users' very different needs; the community web app is not adopted. Iron rule: frontends never talk to the core directly — always through the gateway;
6. **[ADR-006: product lines in three waves](../../../planning/abnk-design/adr/zh-CN/006-product-lines.md)** — savings + consumer lending first (the two most mature Fineract modules), business lending second, supply-chain finance parked on the roadmap. The product line decides where the localization deep water hits first (chart of accounts, interest rules).

## Act Three: The Stack Review (2026-10-26 — three more calls)

7. **[ADR-007: Xinchuang compatibility](../../../planning/abnk-design/adr/zh-CN/007-xinchuang-compatibility.md)** — open-source mainline with a compatibility layer, one code line: protocol standards first (OIDC/S3/Redis protocol/K8s), compatibility shifted left into CI, and Chinese commercial cryptography confined to the gateway. A separate "Xinchuang branch" — a second code line — is explicitly rejected;
8. **[ADR-008: channel-layer stack](../../../planning/abnk-design/adr/zh-CN/008-channel-tech-stack.md)** — Spring Cloud Gateway + React/TypeScript + contract-first (API types are always generated from OpenAPI, never hand-written);
9. **[ADR-009: mobile goes Flutter](../../../planning/abnk-design/adr/zh-CN/009-flutter-mobile.md)** — the **only decision in the ten that openly overturns an earlier one** (Supersedes ADR-008, item 3): mobile banking moves from "thin native shell + H5" to a single Flutter codebase shipping both platforms. The value of a decision log isn't never changing your mind — it's that changes leave a trace, a rationale, and a boundary (only the mobile clause changed; gateway and contract-first stayed).

## The Closer: Why Lay It All Open (2026-11-15)

10. **[ADR-010: repository openness and confidentiality boundaries](../../../planning/abnk-design/adr/zh-CN/010-repository-openness.md)** — **open by default; exactly two boundaries stay closed, each carried by a dedicated repo**:

| Repo | Visibility | Domain |
|---|---|---|
| abnk-asdm | public | Process assets (planning/sprints/ADRs/evidence/tooling — this site's data source) |
| abnk-system | public | System deliverables (infra orchestration/channels/deployment) |
| abnk-devportal | public | Content display (this site) |
| `.github-private` | private | **Secrets boundary**: operational credentials that would compromise production |
| abnk-website | private | **Community-ops boundary**: user PII and team operations |

The core belief: **transparency is the content itself, not a risk to be defended** — deployment topology, port allocation, decision processes, and unfinished states are all part of demonstrating ASDM's capability. Production safety rests on secret isolation, gateway auth, and network rules — **not on topology obscurity** (security through obscurity is explicitly not this project's strategy). Three guardrails back it up: a routing rule for admitting new assets, a standing credential-scan tool gate, and a rule that any change to a repo's visibility must go through a new ADR — no silent drift.

The Dev Portal you are reading is ADR-010's direct corollary — the public content-display domain made real — with one built-in self-restraint: **the portal is a pure renderer**. It renders content and hosts no community features (signup, interaction, stats belong to the community-ops domain, i.e. the abnk-website boundary).

## Three Takeaways About the Mechanism

- **Decisions keep a ledger**: every ADR carries status, date, owner, context, rationale, consequences (risks included), and binding derivative constraints — a call is an auditable engineering record, not a vibe;
- **Reversals leave traces**: ADR-009 superseding exactly one clause of ADR-008 shows how the system handles "plans meet reality" gracefully;
- **Governance is its own exhibit**: the five-repo, two-boundary framework of ADR-010 is precisely why this governance section exists — the documents describe the rules, the project structure enforces them, and each confirms the other.

---

> **Sources**: original portal guide (narrative arrangement only) — **the ADR originals are not rewritten**. The full ADR-001–010 set lives in `workspace/docs/planning/abnk-design/adr/zh-CN/` (linked throughout; the originals are authoritative on facts and wording, and are currently Chinese — English editions may grow per-need via the same locale-routing mechanism as this page).
