---
name: autostop
description: Stop an active bounded-autonomy lease and write handoff state. Use when the human asks to stop, a stop condition fires, or approval is required before continuing.
disable-model-invocation: true
---

Run `python3 .cruise/scripts/cruise_session.py autonomy stop --reason "..."`.

Use this when the human asks to stop autonomy or when any stop condition fires.

Include the concrete stop reason. After stopping, report where `.cruise/next.md`, `.cruise/sessions/latest.md`, and `HANDOFF.md` were written.
