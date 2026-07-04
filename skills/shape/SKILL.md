---
name: shape
description: Find deepening opportunities in a codebase, informed by the domain language in `.cruise/protocol.md`, `.cruise/plan.md`, `.cruise/spec.md`, `.cruise/next.md`, and decisions in `docs/adr/`. Use when the user wants to improve architecture, find refactoring opportunities, consolidate tightly-coupled modules, or make a codebase more testable and AI-navigable.
---

# Improve Codebase Architecture

Surface architectural friction and propose **deepening opportunities** — refactors that turn shallow modules into deep ones. The aim is testability and AI-navigability.

## Glossary

Use these terms exactly in every suggestion. Consistent language is the point — don't drift into "component," "service," "API," or "boundary." Full definitions in [LANGUAGE.md](LANGUAGE.md).

- **Module** — anything with an interface and an implementation (function, class, package, slice).
- **Interface** — everything a caller must know to use the module: types, invariants, error modes, ordering, config. Not just the type signature.
- **Implementation** — the code inside.
- **Depth** — leverage at the interface: a lot of behaviour behind a small interface. **Deep** = high leverage. **Shallow** = interface nearly as complex as the implementation.
- **Seam** — where an interface lives; a place behaviour can be altered without editing in place. (Use this, not "boundary.")
- **Adapter** — a concrete thing satisfying an interface at a seam.
- **Leverage** — what callers get from depth.
- **Locality** — what maintainers get from depth: change, bugs, knowledge concentrated in one place.

Key principles (see [LANGUAGE.md](LANGUAGE.md) for the full list):

- **Deletion test**: imagine deleting the module. If complexity vanishes, it was a pass-through. If complexity reappears across N callers, it was earning its keep.
- **The interface is the test surface.**
- **One adapter = hypothetical seam. Two adapters = real seam.**

This skill is _informed_ by the project's domain model. The domain language gives names to good seams; accepted ADRs record shipped decisions the skill should not re-litigate. Provisional decisions in `.cruise/spec.md` are useful planning context, but they are not settled architecture.

## Process

### 1. Explore

Read the project's domain glossary, `.cruise/protocol.md`, `.cruise/plan.md`, `.cruise/spec.md`, `.cruise/next.md`, and accepted ADRs in the area you're touching first.

Decision-state rule:

- `docs/adr/` is accepted shipped architecture.
- `.cruise/spec.md` `## Provisional decisions` is unshipped planning state.
- A candidate that contradicts an accepted ADR needs an explicit ADR-revisit rationale.
- A candidate that contradicts a provisional decision can simply propose changing the plan.

Then walk the codebase. Prefer native host subagent spawning when available (e.g. Claude Code's Agent tool with `subagent_type=Explore`); otherwise explore directly. Don't follow rigid heuristics — explore organically and note where you experience friction:

- Where does understanding one concept require bouncing between many small modules?
- Where are modules **shallow** — interface nearly as complex as the implementation?
- Where have pure functions been extracted just for testability, but the real bugs hide in how they're called (no **locality**)?
- Where do tightly-coupled modules leak across their seams?
- Which parts of the codebase are untested, or hard to test through their current interface?

Apply the **deletion test** to anything you suspect is shallow: would deleting it concentrate complexity, or just move it? A "yes, concentrates" is the signal you want.

### 2. Present candidates

Present a numbered list of deepening opportunities. For each candidate:

- **Files** — which files/modules are involved
- **Problem** — why the current architecture is causing friction
- **Solution** — plain English description of what would change
- **Benefits** — explained in terms of locality and leverage, and also in how tests would improve

**Use `CONTEXT.md` vocabulary for the domain, and [LANGUAGE.md](LANGUAGE.md) vocabulary for the architecture.** If `CONTEXT.md` defines "Order," talk about "the Order intake module" — not "the FooBarHandler," and not "the Order service."

**ADR conflicts**: if a candidate contradicts an accepted ADR in `docs/adr/`, only surface it when the friction is real enough to warrant revisiting the ADR. Mark it clearly (e.g. _"contradicts ADR-0007 — but worth reopening because…"_). Don't list every theoretical refactor an ADR forbids.

**Provisional conflicts**: if a candidate contradicts `.cruise/spec.md`, say so plainly and recommend whether to update the provisional decision. No ADR revisit is needed because the decision has not shipped.

Do NOT propose interfaces yet. Ask the user: "Which of these would you like to explore?"

### 3. Grilling loop

Once the user picks a candidate, drop into a grilling conversation. Walk the design tree with them — constraints, dependencies, the shape of the deepened module, what sits behind the seam, what tests survive.

Side effects happen inline as decisions crystallize:

- **Naming a deepened module after a concept not in `CONTEXT.md`?** Add the term to `CONTEXT.md` — same discipline as `/grill` (see [CONTEXT-FORMAT.md](../grill/CONTEXT-FORMAT.md)). Create the file lazily if it doesn't exist.
- **Sharpening a fuzzy term during the conversation?** Update `CONTEXT.md` right there.
- **User rejects the candidate with a load-bearing reason?** Offer to record that architecture decision under `.cruise/spec.md` `## Provisional decisions`, framed as: _"Want me to record this so future architecture reviews don't re-suggest it?"_ Only offer when the reason would actually be needed by a future explorer to avoid re-suggesting the same thing — skip ephemeral reasons ("not worth it right now") and self-evident ones. Use the provisional decision guidance in [ADR-FORMAT.md](../grill/ADR-FORMAT.md).
- **The chosen architecture ships?** Promote the relevant provisional decision to an accepted ADR in `docs/adr/` only with the first commit that ships it and only when reversing it would require code changes, migration, user-visible behavior changes, or explanation to a future maintainer.
- **Want to explore alternative interfaces for the deepened module?** See [INTERFACE-DESIGN.md](INTERFACE-DESIGN.md).
