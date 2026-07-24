---
name: tdd
description: Test-driven development with red-green-refactor loop. Use when user wants to build features or fix bugs using TDD, mentions "red-green-refactor", wants integration tests, or asks for test-first development.
---

# Test-Driven Development

## Philosophy

**Core principle**: Tests should verify behavior through public interfaces, not implementation details. Code can change entirely; tests shouldn't.

Use TDD selectively, for behavior that benefits from a test-first feedback loop. Avoid overtesting. Do not force TDD onto trivial changes, exploratory spikes, visual polish, or ambiguous specs where it would create tunnel vision or brittle tests.

**Good tests** are integration-style: they exercise real code paths through public APIs. They describe _what_ the system does, not _how_ it does it. A good test reads like a specification - "user can checkout with valid cart" tells you exactly what capability exists. These tests survive refactors because they don't care about internal structure.

**Bad tests** are coupled to implementation. They mock internal collaborators, test private methods, or reach around the interface to assert an incidental detail the interface already exposes. The warning sign: your test breaks when you refactor, but behavior hasn't changed. If you rename an internal function and tests fail, those tests were testing implementation, not behavior.

See [tests.md](tests.md) for examples and [mocking.md](mocking.md) for mocking guidelines.

## Anti-Pattern: Horizontal Slices

**DO NOT write all tests first, then all implementation.** This is "horizontal slicing" - treating RED as "write all tests" and GREEN as "write all code."

This is especially dangerous for an AI agent:

- You can generate dozens of tests from an imagined design in one shot.
- Those tests prematurely freeze names, data structures, and module boundaries you haven't validated.
- Bulk-generated tests create an illusion of rigor while encoding guesses.
- The implementation gets distorted to satisfy the imagined suite instead of the real problem.
- Review burden explodes before you've learned anything from implementing.

**Correct approach**: Vertical slices via tracer bullets. One behavior → RED → GREEN → learn → next behavior. Each test responds to what the previous cycle taught you. A tracer bullet is a thin _end-to-end_ behavior through the public interface - not necessarily the smallest unit-level function. The first test should prove the relevant path works through the contract its callers use.

```
WRONG (horizontal):
  RED:   test1, test2, test3, test4, test5
  GREEN: impl1, impl2, impl3, impl4, impl5

RIGHT (vertical):
  RED→GREEN→learn: test1→impl1
  RED→GREEN→learn: test2→impl2
  RED→GREEN→learn: test3→impl3
  ...
```

## Workflow

### 1. Planning

When exploring the codebase, use the project's domain glossary so that test names and interface vocabulary match the project's language.

Before writing any code:

- [ ] Identify what interface changes are needed
- [ ] List the behaviors to test (not implementation steps)
- [ ] Prioritize by risk (see below)
- [ ] Identify opportunities for [deep modules](deep-modules.md) (small interface, deep implementation)
- [ ] Design interfaces for [testability](interface-design.md)

Ask: "What should the public interface look like? Which behaviors carry the most risk?"

Confirm interface and test priorities with the user when they're available. When working autonomously, state your assumptions before implementing behavior whose interpretation materially affects the public contract, then proceed.

**You can't test everything, and testing effort should not be spread evenly.** Concentrate defensive testing where a failure is costly or hard to see:

- Domain invariants
- Authorization, authentication, and data visibility
- Money movement and billing
- Irreversible or externally visible side effects
- Data loss, corruption, and migrations
- Transactions and concurrency
- State-machine transitions
- Persistence guarantees
- Audit trails and event publication
- Failures that could stay silent
- Previously observed regressions
- Public contracts used by multiple consumers

Go lighter where failure is cheap and immediately visible:

- Trivial glue code
- Visual polish and rapidly changing UI details
- Exploratory spikes and temporary prototypes
- Obvious pass-through behavior
- Easily reversible changes with immediate failure visibility

Deciding question: **What is the blast radius, and how quickly would a failure become visible?**

**Cheap test generation is not a reason to create low-value tests.** Tests are cheap to write with AI but still expensive to understand, maintain, run, debug, and modify.

### 2. Tracer Bullet

Write ONE test that confirms ONE thing about the system through its public interface:

```
RED:   Write test for first behavior → test fails
GREEN: Implement the smallest general behavior that explains it → test passes
       (the general rule, not the literal example - see GREEN in the loop below)
```

This is your tracer bullet - it proves the path works end-to-end, and what it teaches feeds the same LEARN step before you pick the next behavior.

### 3. Incremental Loop

For each remaining behavior:

```
RED:   Write next test → fails
GREEN: Implement the smallest general behavior that explains it → passes
LEARN: Note what the code taught you; let it shape the next test
```

**GREEN means the smallest _non-speculative general_ behavior that explains the test** - not the literal example, and not speculative machinery:

- Don't hard-code the exact example just to pass. A test asserting a 10% discount on a $100 order is not satisfied by `return 90` - implement the percentage rule the example represents.
- Do implement the obvious general rule the tested behavior represents.
- Don't add anticipated features or flexibility no current test requires - no unused discount categories, config systems, or abstraction layers.

Rules:

- One test at a time
- Only enough general behavior to pass the current test
- Don't anticipate future tests
- Keep tests focused on observable behavior

### 4. Refactor

Refactor after each return to GREEN - inside the loop above, not once at the end. Look for [refactor candidates](refactoring.md):

- [ ] Extract duplication that represents the same stable concept
- [ ] Deepen modules (move complexity behind simple interfaces)
- [ ] Apply SOLID principles where they clarify, not mechanically
- [ ] Consider what new code reveals about existing code
- [ ] Run tests after each refactor step

**Prefer GREEN before refactoring.** While RED, make only narrowly scoped structural changes needed to implement the intended behavior or create a necessary seam: extracting a seam around an external dependency, making an existing interface able to express the behavior, or moving code the current structure directly blocks. Keep unrelated cleanup out of a red-green cycle - no opportunistic renames, reformatting other files, broad architecture changes, or fixing a smell you just happened to notice.

## Fixing Bugs

When fixing a reproducible bug, first add the smallest behavioral test that fails for the bug and would pass for the intended behavior - unless reproducing it in an automated test is impractical or unsafe.

- Test the externally visible failure, not the faulty implementation.
- Prefer the narrowest test level that faithfully catches the regression.
- For production-only incidents, use deterministic substitutes for the conditions you can't reproduce.
- If no stable automated reproduction is possible, document why and add the strongest feasible boundary or invariant test.

## Ambiguous Requirements

TDD needs a known contract. When behavior is unclear:

- Explore, prototype, or run a small shaping step first - don't encode guesses as permanent tests just because TDD was requested.
- Once the behavior is understood, discard exploratory scaffolding and encode the contract that matters.
- A test suite should preserve accepted behavior, not freeze unresolved product questions.

## Checklist Per Cycle

```
[ ] Test describes behavior, not implementation
[ ] Test uses the public interface for its scope
[ ] Test would survive an internal refactor
[ ] Code implements the general rule, not the literal example
[ ] No speculative features or unused flexibility added
```
