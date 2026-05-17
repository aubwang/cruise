# Cruise

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/aubwang/cruise/blob/main/LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![CI](https://github.com/aubwang/cruise/actions/workflows/test.yml/badge.svg)](https://github.com/aubwang/cruise/actions/workflows/test.yml)
[![Standard: Agent Skills](https://img.shields.io/badge/Standard-Agent%20Skills-green.svg)](https://agentskills.io)

Lightweight skills for maintaining context across AI agent sessions. Cruise helps you refine, implement, and hand off work so the next session picks up exactly where you left off. Works with **Claude Code**, **Codex**, **OpenCode**, and any agent that supports the [Agent Skills](https://agentskills.io/) standard.

## In Action

```
$ claude
> implement the burst-window logic on the rate limiter

    reading .cruise/spec.md...
    editing src/middleware/rate_limit.py...
    running pytest tests/rate_limit/... 8 passed
    committed "Add burst-window logic to rate limiter"

    invoking /handoff (slice complete)...
    wrote .cruise/next.md, sessions/2026-05-21-rate-limiter.md

# --- new terminal, fresh session ---

$ claude
> continue

    reading .cruise/next.md...
    picking up the rate limiter. burst-window test is still red - token
    bucket isn't refilling on the edge of the window. threading
    burst_budget through the middleware now, then re-running
    pytest tests/rate_limit/ to confirm.
```

## Why Cruise?

Complex features often span multiple AI sessions. Each time you start a fresh session, you lose the context: goals, completed work, and next steps. Manually catching the agent up is tedious and error-prone.

Cruise solves this by enabling your AI agent to pre-seed its own future sessions with everything it needs. Start a new session, type `continue`, and the agent picks up where it left off.

## Installation

1. Add the Cruise skills to your agent:
   ```bash
   npx skills add aubwang/cruise
   ```
2. Run setup inside your repository:
   ```
   /cruise-setup
   ```

## Skills

| Skill | Purpose |
|---|---|
| `/cruise-setup` | Install or audit Cruise in a repository |
| `/handoff` | Write a continuation checkpoint (`.cruise/next.md`) so the next session resumes cleanly |
| `/grill` | Stress-test ideas, specs, and architectural decisions before building |
| `/zoom-out` | Step back and evaluate recent work from a higher level |
| `/diagnose` | Debug complex errors with a reproduce-hypothesize-fix loop |
| `/tdd` | Enforce test-first development loops |
| `/shape` | Discover high-leverage architectural improvements |

## How It Works

Cruise creates a `.cruise/` directory in your repo with session state and protocol files. The entire directory is gitignored -- cruise is invisible to your repo's git history and regenerated on each setup run.

```
.cruise/
├── protocol.md       # Agent behavioral contract
├── config.json       # Workspace configuration
├── plan.md           # Current active slice
├── spec.md           # Provisional decisions
├── next.md           # Cross-session handoff and next-session anchor
├── nudge.md          # Human-to-agent nudge channel
├── sessions/         # Session history
├── templates/        # Document templates
└── scripts/
    └── cruise_session.py
```

The only repo-visible changes cruise makes are two marker-delimited upserts:
- `.gitignore` -- a managed block that ignores `.cruise/`
- `AGENTS.md` or `CLAUDE.md` -- a protocol fragment telling the agent where to find cruise state

## Core Concepts

### Handoff Protocol
Invoke `/handoff` when a slice is complete, context is getting heavy, or you want to step away. The agent writes `.cruise/next.md` and a session snapshot so the next session can resume cleanly.

### Provisional Decisions and ADRs
Design decisions made during planning live in `.cruise/spec.md` as provisional decisions. A provisional decision is promoted to an accepted ADR in `docs/adr/` only when the implementation ships and reversing it would be costly.

### Parallel Work
Cruise's protocol encourages agents to use subagents when work can be safely parallelized -- Cruise itself doesn't spawn them, but the protocol tells the agent it should. The parent agent retains responsibility for sequencing, conflict resolution, and integration. Cruise tracks durable outcomes, not every subagent attempt.

## Dependencies

Python 3.8+ (standard library only).

## Development

```bash
python3 -m pytest tests/test_cruise_session.py
```

## Acknowledgments

Skills scaffolding and packaging conventions are borrowed from [mattpocock/skills](https://github.com/mattpocock/skills).

## License

[MIT](https://github.com/aubwang/cruise/blob/main/LICENSE)
