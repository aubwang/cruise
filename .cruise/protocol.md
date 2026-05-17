# Cruise Session Protocol

This is the canonical protocol contract for cross-agent coding sessions in this repository.

Critical-path state must never live only in chat context.

## Standing contract

1. At the start of each user turn, read `.cruise/nudge.md` if it exists and is non-empty.
2. Before starting a meaningful slice, update `.cruise/plan.md`.
3. The parent agent owns sequencing, conflict resolution, integration, and discarding candidate output.
4. Plans and roadmap items are mutable intent.
5. ADRs only record accepted shipped decisions with reversal cost.
6. Store important unshipped decisions in `.cruise/spec.md` as provisional decisions.
7. Promote a provisional decision to ADR at the first commit that ships the decision.
8. At a semantic seam or low-context point, suggest handoff.
9. Execute handoff only when the user explicitly invokes/approves it.
10. Handoffs summarize durable outcomes, validation, pending artifacts, and next action.

## ADR rule

- No shipped code, no accepted ADR.
- Create an ADR when reversing the decision would require code changes, migration, user-visible behavior changes, or explanation to a future maintainer.
- During grill or planning, record important but unshipped decisions under `.cruise/spec.md` `## Provisional decisions`.
- When the decision ships, promote it to an accepted ADR if it has reversal cost.

## Bounded autonomy

Default mode is interactive.

Bounded autonomy is allowed only when the human grants an active autonomy lease in `.cruise/autonomy.md`.

The autonomy lease must specify:
- objective,
- acceptance criteria,
- allowed scope,
- out-of-scope items,
- hard endpoint,
- stop conditions,
- approval boundaries.

The agent may not extend its own lease.

Cruise tooling enforces hard endpoints it can measure, such as expiration, iteration budget, and commit budget. Soft stop conditions such as no progress, scope ambiguity, approval boundaries, and acceptance criteria depend on the agent checking honestly and reporting its judgment.

At each iteration boundary, the agent must check:
- `.cruise/nudge.md`,
- lease expiration,
- iteration budget,
- commit budget,
- acceptance criteria,
- validation state,
- approval boundaries,
- no-progress condition.

When any stop condition fires, the agent must stop, write handoff state, and report why it stopped.

## Parallel work

The parent may use native parallel subagents whenever useful.

Cruise tracks durable work state, not every subagent attempt. If parallel work returns and the parent integrates it in the same slice, summarize the completed outcome and validation in the next checkpoint or handoff.

Record process details only when they affect future work, such as unintegrated patches, branches, worktrees, pending external sessions, important failed approaches, or cleanup tasks.

## Spec quality and zoom-out

Before implementation, grill unclear specs against the codebase and existing docs. Record assumptions, open questions, domain terms, decision candidates, provisional decisions, and zoom-out triggers in `.cruise/spec.md` or `.cruise/plan.md`.

At semantic seams, unexpected complexity, repeated test failure, or scope ambiguity, zoom out before continuing. Map the relevant modules, callers, contracts, existing docs, and decisions before making more code changes.

Do not promote spec intent to an ADR until a shipped code change makes the decision costly to reverse.
