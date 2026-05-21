# 🚘 Code on Cruise Control

A lightweight set of skills to seamlessly maintain context across AI agent sessions. Cruise helps you refine, implement, and hand off your ideas and works with **Claude Code**, **Codex**, **OpenCode** and more.

Make your vibe coding sessions durable with automated handoff protocols -- just type `continue` to pick up exactly where you left off, even in a fresh session.

## ❓ Why Cruise?

When working on complex features or large projects, oftentimes you need to create fresh AI sessions to clear token bloat or refresh context. However, doing so usually means manually catching the agent up: restating goals, listing completed tasks, and redefining next steps.

**Cruise** solves this by enabling your AI agent to automatically pre-seed its *own* future sessions with everything it needs to know. All you have to do is spin up a new session, type `go` or `continue`, or really anything that implies some sort of version of "keep going" and let the agent take the wheel.

## 🚀 Installation & Setup

1. Add the Cruise skills package to your agent ecosystem:
   ```bash
   npx skills add aubwang/cruise
   ```
2. Inside the repository where you want to use Cruise, ask your agent to run the configuration protocol:
   ```bash
   /cruise-setup
   ```

## 🛠️ Available Skills & Commands
Once installed, Cruise equips your AI assistant with the following specialized workflows:
- `/cruise-setup` – Install or audit Cruise configurations in a repository.
- `/grill` - Stress-test and document ideas, implementation details, and architectural decisions for your project. I recommend that you run this right after `/cruise-setup` to nail down your design decisions before the auto loop starts.
- `/autostart` / `/autorun` / `/autostop` - Execute bounded, human-approved autonomous coding cycles. Typically you won't need to touch `/autorun` and `/autostop`, those skills are more for the agent but are available in case you need it.
- `/handoff` - Compress the current conversation state and write a durable continuation checkpoint. In auto mode the agent should already do this without needing you to manually invoke it.
- `/zoom-out` - Force the agent to take a step back and evaluate recent work from a bird's eye view. Helpful for preventing tunnel vision!
- `/diagnose` - Debug complex errors using a reproduce -> hypothesize -> fix loop
- `/tdd` - Enforce disciplined, test first development loops for precise feature implementation.
- `/shape` - Discover and implement high-leverage archetectural and structural improvements in your code


## 🏗️ How It Works
When initialized, Cruise generates a neutral, repository-local protocol layout to anchor your AI:
```
.cruise/
├── protocol.md          # Core agent behavioral guidelines
├── config.json          # Workspace configuration parameters
├── templates/           # Custom state, nudge, and plan templates
└── scripts/
    └── cruise_session.py # Zero-dependency session runner
```

During live development, Cruise dynamically creates and updates the following active context assets:
```
├── .cruise/
│   ├── plan.md          # Active execution roadmap
│   ├── spec.md          # Architecture specs & provisional decisions
│   ├── next.md          # Direct behavioral anchor for the next session
│   ├── nudge.md         # Contextual prompt booster
│   └── sessions/        # Historical context logs
└── HANDOFF.md           # The global cross-session bridge file
```

## 🏄 Dependencies
Just have Python!

## 💡 Core Protocols and Ideas

### 🤝 The Handoff Protocol
Invoke `/handoff` whenever a code slice is complete, context windows are reaching capacity, or you want to step away and leave a crystal-clear continuation point.

### 🛡️ Bounded Autonomy
Define your limits on how far you want your agent to go -- how long to work, how many commits to add, how many times to loop, where to stop, and more.

### 👨‍⚖️ Provisional Decisions & ADRs
In this repo/skill, we define Architectural Decision Records (ADRs) as reserved exclusively for immutable, shipped choices carrying high reversal costs.
- Ongoing design decisions made during planning or grilling live inside .cruise/spec.md under ## Provisional decisions.
- A provisional decision is automatically promoted to an accepted ADR only when its corresponding implementation commit ships, or when changing it would require severe structural refactoring or user-facing alterations.


## 🧑‍💻 Development (working on this repo itself)
Run the localized test suite using Python's native test runner:

```python
python3 -m unittest tests/test_cruise_session.py
```

## 📝 Notes & Acknowledgments
- Many of the foundational skills and scaffolding paradigms are borrowed from the excellent [mattpocock/skills](https://github.com/mattpocock/skills).
- Verifed that Cruise works with Claude Code, OpenAI Codex, and OpenCode. Alternate coding harnesses should also work if they support the [Agent Skills](https://agentskills.io/) standard.

## 📄 License
[MIT](https://github.com/aubwang/cruise/blob/main/LICENSE)
