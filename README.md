# Code on Cruise Control

A lightweight set of skills to help you refine and implement your ideas. Make your vibe coding sessions easier with predefined handoff protocols -- just type `continue` to keep going.


## Install

```sh
npx skills add aubwang/cruise
```

Then, inside the repo where you want to use Cruise, ask your agent to run:

```text
/setup
```

`/setup` audits the repo first, then applies the scaffold only when you approve it.

## Skills

- `setup` - install or audit Cruise in a repo
- `handoff` - write durable continuation state
- `grill` - stress-test a plan against docs and code
- `zoom-out` - re-orient around surrounding architecture
- `diagnose` - debug with a reproduce/hypothesize/fix loop
- `tdd` - use restrained test-first development when it helps
- `shape` - find high-leverage architecture improvements
- `autostart` / `autorun` / `autostop` - bounded human-approved autonomous coding

## What It Does

Cruise publishes neutral installable skills under `skills/`.

`setup` installs the repo-local protocol scaffold and root instruction fragments. It does not generate repo-local skill adapter copies.

The canonical skill sources live under `skills/` and are installed with `npx skills`. If you want Claude Code, Codex, and OpenCode to all know the Cruise skills, install the skill package in each agent environment that needs it.

Cruise creates a neutral repo-local protocol root:

```text
.cruise/
  protocol.md
  config.json
  templates/
  scripts/cruise_session.py
```

It can also generate live session files such as:

```text
.cruise/plan.md
.cruise/spec.md
.cruise/next.md
.cruise/nudge.md
.cruise/sessions/
HANDOFF.md
```

The CLI uses only the Python standard library. It does not require `uv`, npm, or a project environment.

This repo does not track local agent runtime/config directories such as `.claude/`, `.agents/`, `.codex/`, or `.opencode/`.

## Handoff

Use `handoff` when a slice is complete, context is getting low, or the agent should stop and leave a clean continuation point.

By default, handoff does not commit. Handoff commits happen only when explicitly requested.

## Autonomy

Bounded autonomy is optional and off by default. Hard caps such as time, iteration, and commit budgets are enforceable; soft stops such as no progress, scope drift, approval boundaries, and acceptance criteria still depend on agent judgment and honest reporting.

## Decisions

ADRs are only for accepted shipped decisions with reversal cost.

Important decisions made during planning or grilling live in:

```md
.cruise/spec.md
## Provisional decisions
```

Promote a provisional decision to an accepted ADR when the first commit ships it and reversing it would require code changes, migration, user-visible behavior changes, or explanation to a future maintainer.

## Development

```sh
python3 -m unittest tests/test_cruise_session.py
```

## Notes
Alot of the skills and scaffolding ideas are borrowed from [mattpocock/skills](https://github.com/mattpocock/skills)

## License

MIT
