---
section: methodology
status: published
locale: en-US
date: 2026-11-16
---
# The ASDM Methodology at a Glance — Three Engineering Disciplines, One Product Stack

> A reader's guide to ASDM (AI-Driven Software Development Methodology) for the international community: what it is, what its three engineering disciplines mean, and how they add up to a product system. Read this first — it is the frame of reference for every iteration record, decision, and piece of evidence on this portal.

## ASDM in One Paragraph

ASDM is an engineering methodology for making AI a reliable contributor to software development. It starts from an honest view of how large language models actually work: **an LLM is, at bottom, a blisteringly fast text-completion engine — no "understanding," just statistical correlations learned from a massive corpus**. That means output quality comes down to two things: the context the model sees, and the tools it can use.

If your experience with AI coding is "great for the first few turns, then it drifts," the gap is not model intelligence. It is this:

1. **The context is wrong** — what the tooling auto-assembles is generic (nearby files, text around the cursor). It knows nothing about your architecture boundaries, conventions, or domain;
2. **The tools are wrong** — traditional dev toolchains were designed for humans: press F5, read a log panel, edit a file. AI can't participate in that loop, so the self-debugging cycle never turns.

The two corresponding moves — **give AI the right context, give AI the right tools** — point to a fundamental paradigm shift: **stop designing systems for humans and start designing them for AI**. ASDM systematizes that shift into three engineering disciplines.

## The Three Disciplines

| # | Discipline | Question it answers | Keywords |
|---|---|---|---|
| 01 | **Knowledge engineering** — operationalized as context engineering | What does the AI know? | Structured knowledge, semantic retrieval, dynamic context assembly |
| 02 | **Harness engineering** | What can the AI do? | Multi-agent orchestration, tool guards, sandboxing, the constrain–verify–repair loop |
| 03 | **Loop engineering** (self-iteration) | How does the AI keep improving? | Live sync with change, feedback loops, incremental updates |

- **Knowledge / context engineering** builds the environment of context the AI works from — the engineering answer to "friendly context."
- **Harness engineering** provides the toolchain and execution environment so the AI can take part in development and deliver reliably — the engineering answer to "friendly tools."
- **Loop engineering** keeps both of them current as the project evolves, so the system gets better with use instead of decaying.

The deep-dive articles are currently published in Chinese ([context engineering](../zh-CN/context-engineering.md), [harness engineering](../zh-CN/harness-engineering.md), [self-iteration](../zh-CN/self-iteration.md)); this overview is their English-language companion.

## A Product System, Not Just Theory

ASDM is a value chain, not a whitepaper:

```
Methodology (theory) → ASDM Platform (management) → TianHuan AI / AgentOrbit (execution)
                                  ↑
                      Training system (the talent-conversion layer)
```

- **Methodology (theory layer)**: the three disciplines — the section you are reading;
- **ASDM Platform (management layer)**: workspace management, asset libraries, engineering-insight dashboards;
- **Execution layer**: agent instance management and runtime interaction — where AI coding agents actually do the work;
- **Training (talent-conversion layer)**: turns the three core capabilities into teachable, practicable, assessable skills, feeding the ecosystem two kinds of talent — **users** (AI-era developers, the "super individuals" who ship end-to-end with ASDM) and **builders** (ASDM FDEs — forward-deployed engineers who design, build, and deliver tailored ASDM tool systems for organizations).

The training curriculum mirrors the disciplines' progression: context engineering (make the AI understand the project), then knowledge + harness (equip the AI with tools), then an end-to-end harness capstone — from "can use" to "can build" to "can teach."

## Verified by Practice

This methodology is not armchair design — the Amazing Bank project on this portal is its full-scale field test, and the training system classifies it as an L3-complexity case (core banking, multi-system integration, security and compliance requirements):

- **Iteration timeline**: Sprint → Part → Phase → Task, every layer planned, gated, and evidenced;
- **Evidence chain**: execution records and verification outputs archived as-is — traceable and auditable;
- **A living self-iteration sample**: the portal's own delivery (planning, decisions, evidence) has been written to the methodology's schema from day one and becomes portal content in real time — **the recursive narrative is a design principle, not a by-product**.

Three deep dives (currently in Chinese, English editions will grow per-need via the same locale-routing mechanism this page itself demonstrates):

1. [上下文工程 — Context engineering](../zh-CN/context-engineering.md)
2. [驾驭工程 — Harness engineering](../zh-CN/harness-engineering.md)
3. [自我迭代 — Self-iteration & the Amazing Bank case](../zh-CN/self-iteration.md)

---

> **Sources** (public material from the asdm-training repo, referenced without altering the originals):
> - `asdm-training/docs/workshops/README.md` (training-system master plan — product-stack layers, talent-conversion layer, the two tracks)
> - `asdm-training/docs/workshops/sessions/20261030-ISS-Public/02-课件/第1天-理论与方法/03-第1天-AI编码工作原理与三大工程（文字版）.md` (how AI coding works, the two moves, the three disciplines)
> - `asdm-training/docs/workshops/tracks/01-asdm-user-track/README.md` (user-track L1–L5 curriculum path)
