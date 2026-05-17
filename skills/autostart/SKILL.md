---
name: autostart
description: Create a bounded-autonomy lease after explicit human approval. Use when the user asks Cruise to run unattended for a defined objective with acceptance criteria, scope, and hard budgets.
disable-model-invocation: true
---

Use `python3 .cruise/scripts/cruise_session.py autonomy start ...` as the protocol entrypoint.

Create a lease only from explicit human instruction. The agent may suggest autonomy mode, but must not start it without human approval.

Before creating the lease, confirm the objective, acceptance criteria, allowed scope, out-of-scope items, time budget, iteration budget, and commit budget. If any of those are missing, ask instead of filling them in.

The tooling enforces hard caps it can measure. Soft stop conditions such as no progress, scope drift, and approval boundaries still depend on the agent checking honestly at each iteration.
