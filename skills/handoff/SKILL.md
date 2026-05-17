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

Run `python3 .cruise/scripts/cruise_session.py handoff --no-commit` unless the user explicitly requested a commit.

If the user explicitly requested a handoff commit, run `python3 .cruise/scripts/cruise_session.py handoff --commit`.

After the command runs, report the paths for `.cruise/next.md`, `.cruise/sessions/latest.md`, and `HANDOFF.md`.
