---
section: overview
status: published
locale: en-US
date: 2026-11-16
---
# The Iteration Timeline, Explained — A Four-Layer Drill-Down

> The portal's core narrative structure is a four-layer drill-down: **Sprint → Part → Phase → Task**. This page explains what each layer means and how to read it — once you know the skeleton, every record on the timeline page has a place to live.

## The Four Layers

```
Sprint (v0.0.1)        one version iteration — the project's timebox
  └── Part             a delivery unit — one independently acceptable batch
        └── Phase      a stage — related tasks with preconditions and exit gates
              └── Task the unit of work — a three-part spec plus per-step acceptance
```

| Layer | Meaning | Typical content | Status scale |
|---|---|---|---|
| **Sprint** | Version iteration | v0.0.1: Fineract core stack → frontend delivery → workspace consolidation → this portal | in progress / done |
| **Part** | Delivery unit | Part01 foundations, Part02 frontend & E2E, Part03 ASDM workspace, Part04 this dev portal | ⏳ → ✅ |
| **Phase** | Stage | e.g. Part04: data layer → content layer → site layer → release layer | ⏳ → ✅ |
| **Task** | Unit of work | Purpose + file-level change list + deliverables, with per-step acceptance criteria | ⏳ → ✅ |

## What a Task Looks Like

Every task follows the same shape (the "three-part spec"): **purpose** (why it exists), **change details** (which files are created or modified), and **execution & acceptance steps** (each step is a verification action with expected output — checked off only after the real run passes). Tasks execute in ID order; the next task cannot start until the current one passes every step. Status is driven by verification results, never by self-report — a direct application of the harness-engineering principle "[specs as gates](../methodology/zh-CN/harness-engineering.md)" (Chinese; English edition growing per-need).

## How to Drill Down

1. **Start at the timeline page** for the full picture — each Part is a segment with phase statuses and task completion at a glance;
2. **Open a Phase plan** — preconditions, task breakdown, known pitfalls: engineering judgment in the raw;
3. **Open a task's evidence** — verification commands with real output, walkthrough records, screenshots: the primary sources behind every conclusion;
4. **Cross-check**: the timeline page and the [metrics dashboard](../../../../index/metrics-v0.0.1.json) are aggregated by the same generator from the same front-matter, so the numbers agree by construction (idempotently recomputable).

## A Worked Example — This Very Portal

Take the portal's own delivery: the [Part04 master plan](../../../Sprints/v0.0.1/part04/zh-CN/v0.0.1-Part04-Plan.md) (Chinese) is the skeleton the timeline renders — Phase 1 (data layer) closed on 2026-11-16, Phase 2 (content layer) is underway, and the page you are reading right now is itself a deliverable of Phase 2, task 2.3. **The portal exhibits its own delivery process — the recursive narrative is a design principle, not a by-product.**

---

> **Sources**: original portal content; the four-layer structure and three-part task spec follow the sprint-document conventions of the abnk-asdm repo (`workspace/docs/Sprints/v0.0.1/part01..04/zh-CN/*-Plan.md`).
