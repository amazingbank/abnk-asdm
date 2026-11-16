---
section: overview
status: published
locale: en-US
date: 2026-11-16
---
# Amazing Bank Dev Portal — Start Here

> What you are looking at is a core-banking project with its entire software engineering process **laid open**: planning, decisions, iterations, evidence, and metrics — all published as-is. This portal produces no content of its own; everything it renders comes from the structured assets of the engineering workspace.

## The Project Behind This Site

Amazing Bank is a core-banking system delivered with the ASDM methodology (AI-Driven Software Development): Apache Fineract at the core, with mobile, back-office, and public-facing channels around it. It doubles as ASDM's flagship L3-complexity reference case — core banking, multi-system integration, and security/compliance requirements all in play.

The question this portal answers: **when an organization claims to be "AI-driven," what does the process actually look like?**

## Eight Sections

| Section | What you'll find |
|---|---|
| [Methodology](../methodology/en-US/index.md) | The three ASDM engineering disciplines — the frame of reference for everything else |
| Planning & decisions | Ten ADRs (architecture decision records) plus per-part decisions, telling the story of why the project looks the way it does |
| Iteration timeline | Sprint → Part → Phase → Task drill-down — how the delivery actually unfolded |
| Task evidence chain | Execution records, verification output, and evidence artifacts per task — traceable and auditable |
| E2E journey | The end-to-end engineering run told in five gated steps, with snapshots, screenshots, and evidence |
| Metrics dashboard | Test figures, LOC curve, evidence density — including honest labels on what isn't done yet |
| Governance & openness | How a project decides what to open-source and where the boundaries are (ADR-010) |
| Reproduction guide | Clone two repos → sync data → build — anyone can rebuild this site |

## Two Reading Principles

1. **Transparency includes transparently showing what's unfinished.** Deferred items, handed-over tasks, and a CI pipeline that hasn't run yet are all labeled as such on the metrics dashboard — nothing is hidden and nothing is inflated. That is this project's honesty rule;
2. **Evidence outranks narrative.** Every claim drills down to raw evidence — command output, screenshots, test reports. If a statement here raises a question, follow its evidence chain.

## Where the Data Comes From

This site is **statically rendered at build time**: a generator in the engineering repo aggregates process assets into an index and metrics that are committed to git (the git history doubles as the audit trail for data trustworthiness). The portal build then performs a read-only copy — zero extraction logic. Anyone who clones the two repositories can reproduce this site exactly; see the reproduction guide.

Start with the [timeline skeleton explainer](./timeline.md) to learn the drill-down structure, or read the [methodology overview](../methodology/en-US/index.md) first to build your frame of reference.

---

> **Sources**: original portal content, written against the section design in the abnk-asdm repo's Part04 plan (`workspace/docs/Sprints/v0.0.1/part04/zh-CN/v0.0.1-Part04-Plan.md`); the L3-case framing follows `asdm-training/docs/workshops/README.md`.
