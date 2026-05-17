---
name: handoff
description: Refresh durable Cruise session state; only commit when the user explicitly requests it.
disable-model-invocation: true
argument-hint: What should the next session focus on?
---

Write a compact handoff so a fresh agent can continue from durable repo state instead of chat history.

A good handoff captures:
- what was decided,
- what is still open,
- which files, issues, PRDs, ADRs, plans, commits, or diffs matter,
- which skills the next session should use, if any,
- what the next session is supposed to do.

Do not duplicate content already captured in other artifacts. Reference those artifacts by path, URL, commit, or diff instead.

If the user passed arguments, treat them as the next session focus and tailor the handoff around that focus.

## Refresh `.cruise/plan.md` first

The handoff command reads `.cruise/plan.md` and bakes its `## Current objective` and `## Current slice` into `.cruise/next.md` and `.cruise/sessions/`. Stale plan.md means a stale handoff that misleads the next agent.

Before running the command, open `.cruise/plan.md` and verify it reflects what just happened and what's next:

- If it still contains the post-setup placeholder (`(not set ...)`), fill it in.
- If it describes a slice that's already done, replace it with the current/next slice.
- If the work moved on but plan.md still names the previous focus, update it.

Only run the handoff command after plan.md is current. The script will also print a `warning:` line if it detects placeholder content; if you see one, fix plan.md and rerun handoff.

## Run the command

Run `python3 .agents/skills/cruise-setup/scripts/cruise_session.py handoff --no-commit` unless the user explicitly requested a commit.

If the user explicitly requested a handoff commit, run `python3 .agents/skills/cruise-setup/scripts/cruise_session.py handoff --commit`.

After the command runs, report the paths for `.cruise/next.md` and `.cruise/sessions/latest.md`. If the command printed a `warning:` line, surface it to the user and refresh plan.md before declaring the handoff done.
