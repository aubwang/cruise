---
name: cruise-setup
description: Install or audit Cruise, then set up repo instructions so domain glossary and decision-state conventions are clear. Run before first use of `grill`, `diagnose`, `tdd`, `shape`, or `zoom-out`.
disable-model-invocation: true
---

# Setup Cruise

Cruise setup **wires the scaffold**. It does not own product planning files and it does not migrate existing docs. After the scaffold is in place this skill walks the user through choosing the right root instruction file, writing the protocol fragment, recording the domain glossary and decision-state conventions, then reconciling any detected planning files (`ROADMAP.md`, `docs/PLAN.md`, etc.) before declaring setup done.

This is a prompt-driven skill that delegates atomic work to `cruise_session.py`. Confirm with the user before each step. Do not skip the reconciliation step — a stale `.cruise/plan.md` will mislead future agents.

## What Cruise owns vs. doesn't own

**Cruise-owned (the scaffold writes these):**

- `.cruise/protocol.md` — Cruise protocol contract
- `.cruise/plan.md` — current active slice for the next session (small, ephemeral)
- `.cruise/spec.md` — provisional unshipped decisions
- `.cruise/next.md`, `.cruise/sessions/`, `.cruise/nudge.md`, etc.
- `.cruise/config.json`

**Repo-owned (Cruise must not write or repurpose these):**

- `ROADMAP.md` — product roadmap
- `docs/PLAN.md` (or `PLAN.md`) — product implementation status / milestones
- `HANDOFF.md` — written by the `handoff` command on first use, but the *meaning* belongs to whatever the repo wants
- `CONTEXT.md` / `CONTEXT-MAP.md`
- `docs/adr/` — accepted shipped ADRs
- `AGENTS.md` / `CLAUDE.md`

If any repo-owned file is missing, leave it missing. Do not create it from a template.

## 0. Bootstrap the protocol script

Resolve this skill's bundled `scripts/cruise_session.py` relative to the skill directory. If `.cruise/scripts/cruise_session.py` is missing or stale, copy the bundled script there and make it executable.

Run `python3 .cruise/scripts/cruise_session.py cruise-setup check` first and show the setup report. The report distinguishes "protocol fragment present" (the Cruise marker block) from "agent-skills block present" (the `## Agent skills` block this skill writes), and surfaces any detected planning files under `## Planning files`.

## 1. Apply the scaffold

Run `python3 .cruise/scripts/cruise_session.py cruise-setup apply` only when the user explicitly approves applying setup changes.

`apply` writes only the Cruise-owned files listed above (under `.cruise/` plus `.cruise/config.json`). It does **not** create `AGENTS.md`, `CLAUDE.md`, `ROADMAP.md`, `HANDOFF.md`, `docs/PLAN.md`, or any other repo-owned file.

The Cruise skills are installed through `npx skills`; setup does not generate repo-local skill adapter copies.

## 2. Choose the root instruction file

Pick the file to edit:

- If `CLAUDE.md` exists, use it.
- Else if `AGENTS.md` exists, use it.
- If both exist as regular files, ask the user whether to keep both or symlink one to the other. The convention is `CLAUDE.md -> AGENTS.md` (single source of truth in AGENTS.md). Only collapse them if the user agrees.
- If neither exists, ask the user which one to create — don't pick for them.

Never create `AGENTS.md` when `CLAUDE.md` already exists (or vice versa). Existing `CLAUDE.md -> AGENTS.md` symlinks are preserved automatically: edits through the symlink land in `AGENTS.md`.

## 3. Write the protocol fragment

Run `python3 .cruise/scripts/cruise_session.py cruise-setup instructions <FILE>` with the chosen file (`AGENTS.md` or `CLAUDE.md`). This upserts the Cruise protocol marker block into that file. It does not touch the rest of the file.

## 4. Configure domain conventions

Record the per-repo conventions that the engineering skills assume:

- **Domain glossary** — whether this repo uses root `CONTEXT.md` or `CONTEXT-MAP.md`
- **Decision state** — where accepted ADRs live and where provisional planning decisions live

Look at the current repo to understand its starting state. Read whatever exists; don't assume:

- `git remote -v` and `.git/config` — is this a GitHub repo? Which one?
- `AGENTS.md` and `CLAUDE.md` at the repo root — is there already an `## Agent skills` section?
- `CONTEXT.md` and `CONTEXT-MAP.md` at the repo root
- `docs/adr/` and any `src/*/docs/adr/` directories for accepted decisions that already shipped
- `.cruise/spec.md` for provisional decisions that are not shipped yet

Summarise what's present and what's missing, then ask:

> Explainer: Some skills (`shape`, `diagnose`, `tdd`) read a `CONTEXT.md` file to learn the project's domain language, `docs/adr/` for accepted decisions that already shipped, and `.cruise/spec.md` for provisional decisions that are still planning state. They need to know whether the repo has one global context or multiple (e.g. a monorepo with separate frontend/backend contexts) so they look in the right place.

- **Single-context** — one `CONTEXT.md` + `docs/adr/` at the repo root. Most repos are this.
- **Multi-context** — `CONTEXT-MAP.md` at the root pointing to per-context `CONTEXT.md` files (typically a monorepo).

Decision rule:

- `docs/adr/` contains accepted ADRs for decisions that have shipped or are already true in the codebase.
- `.cruise/spec.md` `## Provisional decisions` contains important unshipped decisions, rejected ideas, and planning constraints that future agents should remember.
- Do not put proposed ADRs in `docs/adr/`. Promote a provisional decision to an accepted ADR only when the first commit ships it and reversal would be costly.

## 5. Edit the `## Agent skills` block

Show the user a draft and let them edit before writing. If a block already exists, update its contents in-place rather than appending a duplicate. Don't overwrite user edits to surrounding sections.

In the block, name any **repo-owned planning files** the engineering skills should read at session start (typically `ROADMAP.md`, `docs/PLAN.md`, `HANDOFF.md`) so future agents go to the right place for product context.

```markdown
## Agent skills

### Domain glossary

[one-line summary of layout — for example: "single-context: use root `CONTEXT.md`" or "multi-context: use root `CONTEXT-MAP.md` to find relevant context glossaries."]

### Decisions

Accepted shipped ADRs live in `docs/adr/`. Provisional unshipped decisions live in `.cruise/spec.md` under `## Provisional decisions`.

### Planning files

[list the repo-owned planning files agents should consult — e.g. `ROADMAP.md` for product roadmap, `docs/PLAN.md` for implementation status and milestones.]
```

## 6. Reconcile `.cruise/plan.md` (required)

`apply` writes `.cruise/plan.md` as a placeholder ("not set"). If you leave it that way, future agents will follow the placeholder instead of the real plan. Resolve this **before declaring setup done**.

The setup report's `## Planning files` section lists any detected planning docs (`ROADMAP.md`, `docs/PLAN.md`, `PLAN.md`, `HANDOFF.md`, etc.). For each one, ask the user:

1. **Is this still authoritative?** If yes, it stays where it is — Cruise does not move or rewrite it.
2. **Does it contain a current active slice that should be in `.cruise/plan.md`?** If yes, the user (or you, with their approval) copies the slice content into `.cruise/plan.md`.
3. **What should the durable split be?** Confirm and record in the `## Agent skills` block from step 5. The default split is:
   - `.cruise/plan.md` — current active slice (ephemeral, next session)
   - `ROADMAP.md` — product roadmap (longer-term mutable intent)
   - `docs/PLAN.md` — product implementation status / milestones
   - `.cruise/protocol.md` — Cruise protocol details

After this step, `.cruise/plan.md` must either contain a real current slice or have been intentionally left as placeholder with the user's confirmation that there is no active slice yet.

## 7. Audit the rest

Walk the remaining repo state with the user. Surface anything stale; propose moves; let the user decide:

- **CONTEXT.md / CONTEXT-MAP.md** — does the domain glossary reflect the current codebase?
- **`docs/adr/`** — are all entries accepted shipped decisions? Move anything that's still planning out.
- **`.cruise/spec.md`** — does it list the provisional decisions that aren't shipped yet? Carry over anything from prior planning docs.

Don't migrate anything without asking.

## 8. Done

Tell the user the setup is complete, name the durable split that was confirmed in step 6, and which engineering skills will now read from `CONTEXT.md` or `CONTEXT-MAP.md`, `docs/adr/`, and `.cruise/spec.md`. Mention they can edit the `## Agent skills` block later if they change the domain-doc layout.
