---
status: active
created: {{created}}
created_by: human
expires_at: {{expires_at}}
max_iterations: {{max_iterations}}
max_commits: {{max_commits}}
max_cost_usd: null
mode: bounded-autonomy
approval_required_for:
  - deploy
  - publish
  - delete-data
  - force-push
  - dependency-major-upgrade
  - schema-migration
  - secrets-or-credentials
stop_on:
  - acceptance-criteria-met
  - time-expired
  - iteration-budget-hit
  - commit-budget-hit
  - no-progress-2-iterations
  - failing-tests-after-3-repair-attempts
  - ambiguity-that-changes-scope
  - approval-required
---

# Autonomy Lease

## Objective

{{objective}}

## Acceptance criteria

{{acceptance_criteria}}

## Allowed scope

{{allowed_scope}}

## Explicitly out of scope

{{out_of_scope}}

## Enforcement limits

Cruise tooling enforces hard caps it can measure. Soft stop conditions such as no progress, scope drift, approval boundaries, and acceptance criteria depend on the agent checking honestly at each iteration.

## Loop instruction

Work slice by slice. After each iteration:

1. Read `.cruise/nudge.md`.
2. Check whether the autonomy lease is still active.
3. Update `.cruise/plan.md`.
4. Implement the next smallest useful step.
5. Run relevant validation.
6. Commit only if the change is coherent and safe.
7. Update `.cruise/autonomy.log.md`.
8. Update session/handoff state as needed.
9. Check all stop conditions.
10. Continue only if the lease remains active and no stop condition has fired.

When stopping, write:
- `.cruise/next.md`
- `.cruise/sessions/<session-id>.md`
- `.cruise/sessions/latest.md`
- `HANDOFF.md`

Then set `.cruise/autonomy.md` to `status: stopped`.
