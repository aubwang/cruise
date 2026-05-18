---
name: cruise-setup
description: Install or audit Cruise, then set up repo instructions so domain glossary and decision-state conventions are clear. Run before first use of `grill`, `diagnose`, `tdd`, `shape`, or `zoom-out`.
disable-model-invocation: true
---

# Setup Cruise

Bootstrap Cruise first, then configure the repo-specific documentation conventions that the engineering skills assume.

## 0. Bootstrap the protocol

Resolve this skill's bundled `scripts/cruise_session.py` relative to the skill directory. If `.cruise/scripts/cruise_session.py` is missing or stale, copy the bundled script there and make it executable.

Run `python3 .cruise/scripts/cruise_session.py cruise-setup check` first and show the setup report.

Run `python3 .cruise/scripts/cruise_session.py cruise-setup apply` only when the user explicitly approves applying setup changes. Preserve existing repo instructions, existing `CLAUDE.md -> AGENTS.md` symlinks, and existing ADR conventions.

Setup does not generate repo-local skill adapter copies. The skills are installed through `npx skills`; setup only writes the neutral `.cruise/` protocol scaffold and root instruction fragments.

## 1. Configure domain conventions

Record the per-repo conventions that the engineering skills assume:
- **Domain glossary** — whether this repo uses root `CONTEXT.md` or `CONTEXT-MAP.md`
- **Decision state** — where accepted ADRs live and where provisional planning decisions live

This is a prompt-driven skill, not a deterministic script. Explore, present what you found, confirm with the user, then write.

## Process

### 1. Explore

Look at the current repo to understand its starting state. Read whatever exists; don't assume:

- `git remote -v` and `.git/config` — is this a GitHub repo? Which one?
- `AGENTS.md` and `CLAUDE.md` at the repo root — does either exist? Is there already an `## Agent skills` section in either?
- `CONTEXT.md` and `CONTEXT-MAP.md` at the repo root
- `docs/adr/` and any `src/*/docs/adr/` directories for accepted decisions that already shipped
- `.cruise/spec.md` for provisional decisions that are not shipped yet

### 2. Present findings and ask

Summarise what's present and what's missing. Present the follow section(s) **one at a time** — present a section, get the user's answer, then move to the next.

Assume the user does not know what these terms mean. Each section starts with a short explainer (what it is, why these skills need it, what changes if they pick differently). Then show the choices and the default.

**Section: Domain glossary.**

> Explainer: Some skills (`shape`, `diagnose`, `tdd`) read a `CONTEXT.md` file to learn the project's domain language, `docs/adr/` for accepted decisions that already shipped, and `.cruise/spec.md` for provisional decisions that are still planning state. They need to know whether the repo has one global context or multiple (e.g. a monorepo with separate frontend/backend contexts) so they look in the right place.

Confirm the layout:

- **Single-context** — one `CONTEXT.md` + `docs/adr/` at the repo root. Most repos are this.
- **Multi-context** — `CONTEXT-MAP.md` at the root pointing to per-context `CONTEXT.md` files (typically a monorepo).

Decision rule:

- `docs/adr/` contains accepted ADRs for decisions that have shipped or are already true in the codebase.
- `.cruise/spec.md` `## Provisional decisions` contains important unshipped decisions, rejected ideas, and planning constraints that future agents should remember.
- Do not put proposed ADRs in `docs/adr/`. Promote a provisional decision to an accepted ADR only when the first commit ships it and reversal would be costly.

### 3. Confirm and edit

Show the user a draft of:

- The `## Agent skills` block to add to whichever of `CLAUDE.md` / `AGENTS.md` is being edited (see step 4 for selection rules)

Let them edit before writing.

### 4. Write

**Pick the file to edit:**

- If `CLAUDE.md` exists, edit it.
- Else if `AGENTS.md` exists, edit it.
- If neither exists, ask the user which one to create — don't pick for them.

Never create `AGENTS.md` when `CLAUDE.md` already exists (or vice versa) — always edit the one that's already there. If both files exist, symlink them together.

If an `## Agent skills` block already exists in the chosen file, update its contents in-place rather than appending a duplicate. Don't overwrite user edits to the surrounding sections.

The block:

```markdown
## Agent skills

### Domain glossary

[one-line summary of layout — for example: "single-context: use root `CONTEXT.md`" or "multi-context: use root `CONTEXT-MAP.md` to find relevant context glossaries."]

### Decisions

Accepted shipped ADRs live in `docs/adr/`. Provisional unshipped decisions live in `.cruise/spec.md` under `## Provisional decisions`.
```

### 5. Done

Tell the user the setup is complete and which engineering skills will now read from `CONTEXT.md` or `CONTEXT-MAP.md`, `docs/adr/`, and `.cruise/spec.md`. Mention they can edit the `## Agent skills` block later if they change the domain-doc layout.
