---
title: "ai-design-system-demo-app: Decisions"
type: decision-log
date: 2026-07-13
updated: 2026-10-29
source: Written at the pauses in the milestone sequence (the proposal pick, the plan's out-of-scope list, a change of direction mid-session, the close of a merged branch)
description: Why each decision was made and what was passed over, one entry per decision, plus the outcome, lesson, and client words at the close of every milestone. Read by the timelapse record and by the case study.
related: [PRD.md, DESIGN.md]
tags: [decisions, ai-design-system-demo-app]
---

# ai-design-system-demo-app: Decisions

## Decisions

One decision per entry, numbered in the order they were made. `Instead` names the road not taken and is never blank when a proposal was rejected. A later decision that replaces an earlier one says so in `Supersedes` and leaves the old entry in place. The entry shape is in the `stack-markdown` skill's `template/decision-log.md`.

### D001: Accept the zod findings under @figma/code-connect
- Date: 2026-10-29
- Branch: fix-npm-audit
- Area: stack
- Because: npm audit flags zod 3.x (high, fixed only in 4.6.6) through `@figma/code-connect`, and no code-connect release (2.1.0 is the newest) depends on zod 4. Code-connect is a dev-only command-line tool for publishing the Code Connect mappings; it never reaches the built site, and the memory issue needs oversized input that only Doug would hand it. GitHub's Dependabot showed no open alert for it on 2026-10-29. Revisit when a code-connect release moves to zod 4.
- Instead: An npm `overrides` entry forcing zod 4 under code-connect, passed over because code-connect is written against zod 3's API and the override would sit hidden under every later upgrade.
- Supersedes: none

## Milestone close

One entry per merged branch, written before the merge from Doug's answers. "none" is a valid answer for every line; an invented answer is not.
