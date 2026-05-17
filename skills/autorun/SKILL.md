---
name: autorun
description: Continue work under an existing bounded-autonomy lease. Use only when `.cruise/autonomy.md` is active and the human has already approved the lease boundaries.
disable-model-invocation: true
---

Use `python3 .cruise/scripts/cruise_session.py autonomy run` as the protocol entrypoint.

Do not run autonomy unless `.cruise/autonomy.md` has `status: active` and the human approved the lease.

Run one bounded iteration at a time. Stop and write handoff state when any lease endpoint or stop condition fires, when `.cruise/nudge.md` asks the agent to stop, or when continuing would require approval outside the lease.

Hard caps are enforced where the script can measure them. Soft stop conditions such as no progress, scope drift, and approval boundaries require explicit agent judgment and reporting.
