---
name: handoff
description: Write a cross-session handoff — refresh `.cruise/next.md` and a session snapshot so the next session resumes cleanly.
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

## Write the summary, then run the command

The handoff command is the `cruise_session.py` script in the sibling `cruise-setup` skill's `scripts/` directory. Resolve it relative to where these skill files are installed: for `npx skills` installs that is `.agents/skills/cruise-setup/scripts/cruise_session.py`; for Claude Code plugin installs it is under the plugin root. `<script>` below means that path.

1. Write the handoff summary to `.cruise/handoff-summary.md` with these sections:
   - `## Summary` — what was decided, open threads, which files/PRs/ADRs/commits matter, which skills the next session should use.
   - `## Pending artifacts` — work products still in flight (unmerged PRs, changes not yet landed, docs still to write).
   - `## Next action` — what the next session should do first.

   If the user passed arguments (next-session focus), weave that focus into `## Summary` and `## Next action`.
2. Run `python3 <script> handoff --summary-file .cruise/handoff-summary.md --slug <short-topic-slug>` with a short kebab-case slug for the session topic. The command bakes the summary into `.cruise/next.md` and the session snapshot. It writes only gitignored `.cruise/` files.
3. Report the paths for `.cruise/next.md` and `.cruise/sessions/latest.md`. If the command printed a `warning:` line, surface it to the user and refresh plan.md before declaring the handoff done.
