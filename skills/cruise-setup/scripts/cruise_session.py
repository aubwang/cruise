#!/usr/bin/env python3
"""Repo-local session handoff and coordination protocol tooling."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import tempfile
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path


def default_root() -> Path:
    explicit = os.environ.get("CRUISE_ROOT")
    if explicit:
        return Path(explicit).resolve()
    path = Path(__file__).resolve()
    if path.parent.name == "scripts" and path.parent.parent.name == ".cruise":
        return path.parents[2]
    return Path.cwd().resolve()


ROOT = default_root()
CRUISE = ROOT / ".cruise"
SESSIONS = CRUISE / "sessions"
TEMPLATES = CRUISE / "templates"
CONFIG_PATH = CRUISE / "config.json"
DEFAULT_ADR_DIR = "docs/adr"


DEFAULT_CONFIG = {
    "protocol_root": ".cruise",
    "adr_dir": DEFAULT_ADR_DIR,
    "root_instruction_files": ["AGENTS.md", "CLAUDE.md"],
}

PROTOCOL_MARKER_START = "<!-- cruise-session-protocol:start -->"
PROTOCOL_MARKER_END = "<!-- cruise-session-protocol:end -->"

GITIGNORE_MARKER_START = "# cruise-gitignore:start"
GITIGNORE_MARKER_END = "# cruise-gitignore:end"

CRUISE_GITIGNORE_FRAGMENT = f"""{GITIGNORE_MARKER_START}
# Managed by cruise-setup. Cruise session state — ephemeral, per-clone.
.cruise/plan.md
.cruise/spec.md
.cruise/next.md
.cruise/nudge.md
.cruise/nudges.log.md
.cruise/autonomy.md
.cruise/autonomy.log.md
.cruise/debug/
.cruise/sessions/*
!.cruise/sessions/.gitkeep
HANDOFF.md
{GITIGNORE_MARKER_END}
"""


CLAUDE_FRAGMENT = f"""{PROTOCOL_MARKER_START}
Read `.cruise/protocol.md` at session start.
At the start of each user turn, check `.cruise/nudge.md`.
Use `.cruise/plan.md` for the current slice plan.
Use `.cruise/sessions/` and `.cruise/next.md` for handoff.
Suggest `/handoff` at semantic seams or low-context points.
Do not run handoff commits unless the user explicitly requests it.
{PROTOCOL_MARKER_END}
"""

AGENTS_FRAGMENT = f"""{PROTOCOL_MARKER_START}
Read `.cruise/protocol.md` before work.
At the start of each user turn, check `.cruise/nudge.md`.
Use `.cruise/plan.md` for the current slice plan.
Use handoff/checkpoint state for durable outcomes, pending artifacts, and next action.
Suggest `$handoff` at semantic seams or low-context points.
Do not run handoff commits unless the user explicitly requests it.
{PROTOCOL_MARKER_END}
"""

PROTOCOL_MD = """# Cruise Session Protocol

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
"""

PLAN_MD = """# Cruise Plan

This file is the **current active slice** for the next session. Replace this
placeholder during setup or before the first session that uses
`.cruise/plan.md`. Longer-term product roadmap and implementation status
belong in repo-owned files (typically `ROADMAP.md` and `docs/PLAN.md`), not
here.

## Current objective

(not set — replace before starting a slice)

## Current slice

(not set)

## Pending artifacts

(none)

## Verification

(not set)
"""

NEXT_TEMPLATE = """Read `.cruise/protocol.md`, `.cruise/sessions/latest.md`, `.cruise/plan.md`, `.cruise/spec.md`, `.cruise/nudge.md`, and any repo planning docs listed in the `## Agent skills` block of `AGENTS.md` or `CLAUDE.md` (typically `HANDOFF.md`, `ROADMAP.md`, `docs/PLAN.md`).

Then summarize:
1. current objective,
2. latest committed state,
3. provisional decisions,
4. pending artifacts,
5. active nudge,
6. next concrete step.

Do not start implementation until you have confirmed the next concrete step.
"""

SESSION_TEMPLATE = """---
session_id: {{session_id}}
parent_session: {{parent_session}}
started: {{started}}
ended: {{ended}}
chunks: []
commits: []
next_prompt_path: .cruise/next.md
---

## Summary

{{summary}}

## Current state

{{current_state}}

## Decisions shipped

{{decisions}}

## Provisional decisions

{{provisional_decisions}}

## Pending artifacts

{{pending_artifacts}}

## Next recommended action

{{next_action}}
"""

ADR_TEMPLATE = """---
id: {{id}}
status: accepted
date: {{date}}
supersedes: null
superseded_by: null
commit: {{commit}}
deciders: []
---

# ADR {{id}}: {{title}}

## Context

## Decision

## Consequences

## Reversal cost
"""

AUTONOMY_TEMPLATE = """---
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
"""

AUTONOMY_INACTIVE = """---
status: inactive
created: null
created_by: null
expires_at: null
max_iterations: null
max_commits: null
max_cost_usd: null
mode: bounded-autonomy
---

# Autonomy Lease

No active autonomy lease.
"""

AUTONOMY_LOG = """# Autonomy Log

Append-only bounded-autonomy checkpoints.
"""

NUDGES_LOG = """# Nudge Log

Append-only nudge history.
"""

SPEC_MD = """# Cruise Spec Notes

## Spec confidence

Status: ungrilled

## Assumptions

_pending_

## Open questions

_pending_

## Domain terms

_pending_

## Decision candidates

_pending_

## Provisional decisions

_pending_

## Zoom-out triggers

- Scope ambiguity.
- Unexpected cross-module impact.
- Repeated validation failure.
- A decision appears to have reversal cost.
"""


def now() -> datetime:
    return datetime.now(timezone.utc)


def utc_stamp() -> str:
    return now().replace(microsecond=0).isoformat().replace("+00:00", "Z")


def session_id() -> str:
    return now().strftime("%Y-%m-%dT%H-%M-%S") + "-" + uuid.uuid4().hex[:8]


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as tmp:
            tmp.write(text)
        umask = os.umask(0)
        os.umask(umask)
        os.chmod(tmp_name, 0o666 & ~umask)
        os.replace(tmp_name, path)
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def ensure_file(path: Path, text: str) -> bool:
    if path.exists():
        return False
    atomic_write(path, text)
    return True


def json_text(data: dict[str, object]) -> str:
    return json.dumps(data, indent=2, sort_keys=True) + "\n"


def find_adr_candidates() -> list[str]:
    candidates = ["docs/adr", "docs/adrs", "adr", "adrs", "decisions", "docs/decisions"]
    return [candidate for candidate in candidates if (ROOT / candidate).exists()]


PLANNING_DOC_CANDIDATES = [
    "ROADMAP.md",
    "docs/ROADMAP.md",
    "docs/roadmap.md",
    "PLAN.md",
    "docs/PLAN.md",
    "docs/plan.md",
    "HANDOFF.md",
]


def find_planning_docs() -> list[str]:
    return [candidate for candidate in PLANNING_DOC_CANDIDATES if (ROOT / candidate).exists()]


def extract_subsection(text: str, heading: str, level: int) -> str:
    prefix = "#" * level
    pattern = re.compile(
        rf"^{re.escape(prefix)} {re.escape(heading)}\s*\n(.*?)(?=^#{{1,{level}}} |\Z)",
        re.DOTALL | re.MULTILINE,
    )
    match = pattern.search(text)
    return match.group(1).strip() if match else ""


def planning_files_warning() -> str | None:
    detected = find_planning_docs()
    if not detected:
        return None
    for name in ["CLAUDE.md", "AGENTS.md"]:
        path = ROOT / name
        if not path.exists():
            continue
        text = read_text(path)
        if PROTOCOL_MARKER_START not in text:
            continue
        agent_skills = extract_subsection(text, "Agent skills", 2)
        if not agent_skills:
            return (
                f"warning: planning files detected but `## Agent skills` block is missing in {name}; "
                f"reconcile per cruise-setup step 6 by adding a `### Planning files` subsection naming "
                f"{', '.join(detected)}."
            )
        planning_section = extract_subsection(agent_skills, "Planning files", 3)
        missing = [doc for doc in detected if Path(doc).name not in planning_section]
        if missing:
            return (
                f"warning: detected planning file(s) {', '.join(missing)} not named under "
                f"`### Planning files` in {name}; reconcile per cruise-setup step 6."
            )
        return None
    return None


def default_config() -> dict[str, object]:
    config = dict(DEFAULT_CONFIG)
    candidates = find_adr_candidates()
    if candidates:
        config["adr_dir"] = candidates[0]
    return config


def load_config() -> dict[str, object]:
    config = default_config()
    if CONFIG_PATH.exists():
        try:
            loaded = json.loads(read_text(CONFIG_PATH))
        except json.JSONDecodeError:
            loaded = {}
        if isinstance(loaded, dict):
            config.update(loaded)
    return config


def migrate_config() -> None:
    if not CONFIG_PATH.exists():
        return
    try:
        loaded = json.loads(read_text(CONFIG_PATH))
    except json.JSONDecodeError:
        return
    if not isinstance(loaded, dict):
        return
    if "targets" in loaded:
        loaded.pop("targets", None)
        atomic_write(CONFIG_PATH, json_text(loaded))


def adr_dir() -> Path:
    value = load_config().get("adr_dir", DEFAULT_ADR_DIR)
    return ROOT / str(value)


def path_label(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def render(template: str, values: dict[str, str]) -> str:
    out = template
    for key, value in values.items():
        out = out.replace("{{" + key + "}}", value)
    return out


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    raw = text[4:end]
    body = text[end + 5 :]
    data: dict[str, str] = {}
    for line in raw.splitlines():
        if not line or line.startswith(" ") or line.startswith("-"):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip()
    return data, body


def replace_frontmatter(text: str, updates: dict[str, str]) -> str:
    if not text.startswith("---\n"):
        lines = ["---"]
        lines.extend(f"{key}: {value}" for key, value in updates.items())
        lines.append("---")
        return "\n".join(lines) + "\n\n" + text
    end = text.find("\n---\n", 4)
    if end == -1:
        return text
    raw = text[4:end]
    body = text[end + 5 :]
    seen: set[str] = set()
    out_lines: list[str] = []
    for line in raw.splitlines():
        stripped = line.strip()
        if ":" in line and not line.startswith(" ") and not stripped.startswith("-"):
            key = line.split(":", 1)[0].strip()
            if key in updates:
                out_lines.append(f"{key}: {updates[key]}")
                seen.add(key)
                continue
        out_lines.append(line)
    for key, value in updates.items():
        if key not in seen:
            out_lines.append(f"{key}: {value}")
    return "---\n" + "\n".join(out_lines) + "\n---\n" + body


def upsert_marked(path: Path, fragment: str, start: str, end: str) -> None:
    current = read_text(path)
    if start in current and end in current:
        pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.DOTALL)
        updated = pattern.sub(fragment.strip(), current)
    else:
        prefix = current.rstrip() + "\n\n" if current.strip() else ""
        updated = prefix + fragment.strip() + "\n"
    write_path = path.resolve(strict=False) if path.is_symlink() else path
    atomic_write(write_path, updated)


def upsert_protocol_fragment(path: Path, fragment: str) -> None:
    upsert_marked(path, fragment, PROTOCOL_MARKER_START, PROTOCOL_MARKER_END)


def append_log(path: Path, title: str, lines: list[str]) -> None:
    existing = read_text(path)
    if existing and not existing.endswith("\n"):
        existing += "\n"
    block = [f"\n## {utc_stamp()} {title}"]
    block.extend(lines)
    atomic_write(path, existing + "\n".join(block) + "\n")


def shell(args: list[str], check: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=check,
    )


def in_git_repo() -> bool:
    return shell(["git", "rev-parse", "--is-inside-work-tree"]).returncode == 0


def git_status_summary() -> str:
    if not in_git_repo():
        return "Not a git repository."
    result = shell(["git", "status", "--porcelain"])
    status = result.stdout.strip()
    return status if status else "Working tree clean."


def latest_commits() -> str:
    if not in_git_repo():
        return "Not a git repository."
    result = shell(["git", "log", "--oneline", "-5"])
    return result.stdout.strip() or "No commits yet."


def latest_session_id() -> str:
    latest = read_text(SESSIONS / "latest.md")
    match = re.search(r"session_id:\s*([A-Za-z0-9_.:-]+)", latest)
    if match:
        return match.group(1)
    return "null"


def active_adr_lines() -> list[str]:
    current_adr_dir = adr_dir()
    if not current_adr_dir.exists():
        return []
    lines: list[str] = []
    for path in sorted(current_adr_dir.glob("*.md")):
        data, body = parse_frontmatter(read_text(path))
        if data.get("status") != "accepted":
            continue
        title = body.splitlines()[0].strip("# ").strip() if body.splitlines() else path.stem
        lines.append(f"- `{path_label(path)}`: {title}")
    return lines


def section_after_heading(text: str, heading: str) -> str:
    pattern = re.compile(rf"^## {re.escape(heading)}\n\n(.*?)(?:\n## |\Z)", re.DOTALL | re.MULTILINE)
    match = pattern.search(text)
    if not match:
        return ""
    return match.group(1).strip()


def provisional_decisions() -> str:
    text = section_after_heading(read_text(CRUISE / "spec.md"), "Provisional decisions")
    if not text or text.strip() == "_pending_":
        return "None."
    return text


def current_objective() -> str:
    plan = read_text(CRUISE / "plan.md")
    objective = section_after_heading(plan, "Current objective")
    if objective:
        return objective
    roadmap = read_text(ROOT / "ROADMAP.md")
    return section_after_heading(roadmap, "v1") or "No current objective recorded."


def next_action() -> str:
    plan = read_text(CRUISE / "plan.md")
    current = section_after_heading(plan, "Current slice")
    if current:
        first = next((line.strip("- ").strip() for line in current.splitlines() if line.strip()), "")
        if first:
            return first
    return "Confirm the next concrete step from `.cruise/next.md`."


def write_next(summary: str, pending_artifacts: str, nudge: str, action: str) -> None:
    body = NEXT_TEMPLATE.rstrip() + "\n\n## Current handoff context\n\n"
    body += f"- Current objective: {current_objective()}\n"
    body += f"- Latest committed state: {latest_commits().splitlines()[0] if latest_commits() else 'Unknown'}\n"
    body += f"- Pending artifacts: {pending_artifacts or 'None'}\n"
    body += f"- Active nudge: {nudge or 'None'}\n"
    body += "- Provisional decisions: See `.cruise/spec.md` `## Provisional decisions`.\n"
    body += f"- Next concrete step: {action}\n"
    body += f"\n## Summary\n\n{summary}\n"
    atomic_write(CRUISE / "next.md", body)


def refresh_handoff(session_path: Path, pending_artifacts: str, nudge: str, action: str) -> None:
    adrs = "\n".join(active_adr_lines()) or "None."
    commits = latest_commits()
    content = f"""# Handoff

This file is a generated/current-state index. The canonical source of truth is `.cruise/protocol.md` plus the files under `.cruise/`.

## Current objective

{current_objective()}

## Latest commits

{commits}

## Active ADRs

{adrs}

## Provisional decisions

{provisional_decisions()}

## Pending artifacts

{pending_artifacts or "None."}

## Active nudge

{nudge or "None."}

## Latest session

`{session_path.relative_to(ROOT)}`

## Next action

{action}

## Next prompt

See `.cruise/next.md`.
"""
    atomic_write(ROOT / "HANDOFF.md", content)


def write_session(commit_requested: bool) -> Path:
    sid = session_id()
    parent = latest_session_id()
    status = git_status_summary()
    nudge = read_text(CRUISE / "nudge.md").strip()
    pending_artifacts = "None."
    adr_lines = active_adr_lines()
    decisions = "\n".join(adr_lines) if adr_lines else "None."
    action = next_action()
    summary = "Session handoff refreshed from durable Cruise protocol state."
    current_state = "\n".join(
        [
            f"Current objective: {current_objective()}",
            "",
            "Git status before commit attempt:",
            "```",
            status,
            "```",
            "",
            f"Commit requested: {'yes' if commit_requested else 'no'}",
        ]
    )
    write_next(summary, pending_artifacts, nudge, action)
    content = render(
        SESSION_TEMPLATE,
        {
            "session_id": sid,
            "parent_session": parent,
            "started": utc_stamp(),
            "ended": utc_stamp(),
            "summary": summary,
            "current_state": current_state,
            "decisions": decisions,
            "provisional_decisions": provisional_decisions(),
            "pending_artifacts": pending_artifacts,
            "next_action": action,
        },
    )
    session_path = SESSIONS / f"{sid}.md"
    atomic_write(session_path, content)
    latest = f"""# Latest Cruise Session

session_id: {sid}
path: {session_path.relative_to(ROOT)}
updated: {utc_stamp()}

## Summary

{summary}

## Next action

{action}
"""
    atomic_write(SESSIONS / "latest.md", latest)
    refresh_handoff(session_path, pending_artifacts, nudge, action)
    return session_path


def maybe_commit() -> None:
    if not in_git_repo():
        print("No git repository found; wrote handoff files and skipped commit.")
        return
    paths = [
        ".cruise",
        "HANDOFF.md",
        "ROADMAP.md",
        str(adr_dir().relative_to(ROOT)) if adr_dir().is_relative_to(ROOT) else DEFAULT_ADR_DIR,
        "CLAUDE.md",
        "AGENTS.md",
        "README.md",
    ]
    existing = [path for path in paths if (ROOT / path).exists()]
    if existing:
        add = shell(["git", "add", *existing])
        if add.returncode != 0:
            raise SystemExit(add.stderr.strip() or "git add failed")
    status = shell(["git", "status", "--porcelain"]).stdout.strip()
    if not status:
        print("No changes to commit.")
        return
    commit = shell(["git", "commit", "-m", "chore: update AI session handoff"])
    if commit.returncode != 0:
        raise SystemExit(commit.stderr.strip() or "git commit failed")
    print(commit.stdout.strip())


def chmod_if_exists(path: Path) -> None:
    if path.exists():
        path.chmod(path.stat().st_mode | 0o111)


def init_common_files() -> None:
    for path in [CRUISE, SESSIONS, TEMPLATES, CRUISE / "scripts"]:
        path.mkdir(parents=True, exist_ok=True)
    ensure_file(CONFIG_PATH, json_text(default_config()))
    migrate_config()
    current_adr_dir = adr_dir()
    current_adr_dir.mkdir(parents=True, exist_ok=True)
    ensure_file(CRUISE / "protocol.md", PROTOCOL_MD)
    ensure_file(CRUISE / "plan.md", PLAN_MD)
    ensure_file(CRUISE / "spec.md", SPEC_MD)
    ensure_file(CRUISE / "nudge.md", "")
    ensure_file(CRUISE / "nudges.log.md", NUDGES_LOG)
    ensure_file(SESSIONS / ".gitkeep", "")
    ensure_file(SESSIONS / "latest.md", "# Latest Cruise Session\n\nNo session handoff has been written yet.\n")
    ensure_file(CRUISE / "next.md", NEXT_TEMPLATE)
    ensure_file(TEMPLATES / "session.md", SESSION_TEMPLATE)
    ensure_file(TEMPLATES / "adr.md", ADR_TEMPLATE)
    ensure_file(TEMPLATES / "next.md", NEXT_TEMPLATE)
    ensure_file(TEMPLATES / "spec.md", SPEC_MD)
    ensure_file(TEMPLATES / "autonomy.md", AUTONOMY_TEMPLATE)
    ensure_file(CRUISE / "autonomy.md", AUTONOMY_INACTIVE)
    ensure_file(CRUISE / "autonomy.log.md", AUTONOMY_LOG)
    ensure_file(current_adr_dir / ".gitkeep", "")


SKILL_NAMES = [
    "handoff",
    "cruise-setup",
    "grill",
    "zoom-out",
    "diagnose",
    "tdd",
    "shape",
    "autostart",
    "autorun",
    "autostop",
]


def candidate_skills_roots(value: str | None = None) -> list[Path]:
    candidates: list[Path] = []
    if value:
        candidates.append(Path(value))
    env = os.environ.get("CRUISE_SKILLS_ROOT")
    if env:
        candidates.append(Path(env))
    script = Path(__file__).resolve()
    if script.parent.name == "scripts" and script.parent.parent.name == "cruise-setup":
        candidates.append(script.parents[2])
    candidates.append(ROOT / "skills")
    return [path.resolve() for path in candidates]


def resolve_skills_root(value: str | None = None, required: bool = False) -> Path | None:
    for path in candidate_skills_roots(value):
        if all((path / name / "SKILL.md").exists() for name in SKILL_NAMES):
            return path
    if required:
        raise SystemExit(
            "Cannot find Cruise skill sources under `skills/`. "
            "Set `CRUISE_SKILLS_ROOT` only when running package maintenance from a nonstandard location."
        )
    return None


def sync_package_skills() -> None:
    skills_root = resolve_skills_root(str(ROOT / "skills"), required=True)
    missing = [name for name in SKILL_NAMES if not (skills_root / name / "SKILL.md").exists()]
    if missing:
        raise SystemExit("Missing installable skill folders: " + ", ".join(missing))
    script_path = skills_root / "cruise-setup" / "scripts" / "cruise_session.py"
    atomic_write(script_path, read_text(CRUISE / "scripts" / "cruise_session.py"))
    chmod_if_exists(script_path)
    for path in (skills_root / "diagnose" / "scripts").glob("*"):
        chmod_if_exists(path)


INSTRUCTION_FRAGMENTS = {"CLAUDE.md": CLAUDE_FRAGMENT, "AGENTS.md": AGENTS_FRAGMENT}


def write_instructions(path: Path) -> None:
    fragment = INSTRUCTION_FRAGMENTS.get(path.name, AGENTS_FRAGMENT)
    upsert_protocol_fragment(path, fragment)


AGENT_SKILLS_HEADING = "## Agent skills"


def instruction_file_lines() -> list[str]:
    lines: list[str] = []
    for name in ["AGENTS.md", "CLAUDE.md"]:
        path = ROOT / name
        if path.is_symlink():
            target = os.readlink(path)
            state = f"symlink -> {target}"
        elif path.exists():
            state = "exists"
        else:
            state = "missing"
        text = read_text(path)
        protocol = "protocol fragment present" if PROTOCOL_MARKER_START in text else "protocol fragment missing"
        agent_skills = "agent-skills block present" if AGENT_SKILLS_HEADING in text else "agent-skills block missing"
        lines.append(f"- {name}: {state}, {protocol}, {agent_skills}")
    if (ROOT / "AGENTS.md").exists() and (ROOT / "CLAUDE.md").is_symlink():
        try:
            if (ROOT / "CLAUDE.md").resolve() == (ROOT / "AGENTS.md").resolve():
                lines.append("- CLAUDE.md -> AGENTS.md symlink detected.")
        except FileNotFoundError:
            lines.append("- CLAUDE.md is a broken symlink.")
    return lines


def setup_report() -> str:
    lines = ["# Cruise Setup Report", ""]
    config = load_config()
    lines.append("## Protocol")
    for path in [
        CRUISE / "protocol.md",
        CONFIG_PATH,
        CRUISE / "plan.md",
        CRUISE / "spec.md",
        CRUISE / "next.md",
        CRUISE / "nudge.md",
    ]:
        state = "present" if path.exists() else "missing"
        lines.append(f"- {path_label(path)}: {state}")
    gitignore_text = read_text(ROOT / ".gitignore")
    if GITIGNORE_MARKER_START in gitignore_text:
        lines.append("- .gitignore: cruise block present")
    elif gitignore_text:
        lines.append("- .gitignore: present, cruise block missing")
    else:
        lines.append("- .gitignore: missing")
    lines.append("")
    lines.append("## Configuration")
    lines.append(f"- adr_dir: {config.get('adr_dir', DEFAULT_ADR_DIR)}")
    candidates = find_adr_candidates()
    if candidates:
        lines.append(f"- detected ADR-like directories: {', '.join(candidates)}")
    else:
        lines.append("- detected ADR-like directories: none")
    if len(candidates) > 1:
        lines.append("- warning: multiple ADR-like directories exist; set `.cruise/config.json` explicitly if needed.")
    lines.append("")
    lines.append("## Planning files")
    planning_docs = find_planning_docs()
    if planning_docs:
        lines.append(f"- detected: {', '.join(planning_docs)}")
        lines.append("- reconcile with `.cruise/plan.md` (current active slice). Cruise does not own `ROADMAP.md`, `docs/PLAN.md`, or similar product files — leave them under repo ownership.")
        warning = planning_files_warning()
        if warning:
            lines.append(f"- {warning}")
    else:
        lines.append("- detected: none")
    lines.append("")
    lines.append("## Root Instructions")
    lines.extend(instruction_file_lines())
    lines.append("")
    lines.append("## Skills")
    lines.append("- repo-local adapter skill copies are not generated")
    lines.append("- install Cruise skills with `npx skills@latest add aubwang/cruise` for each agent environment that needs them")
    lines.append("")
    lines.append("## Runtime")
    lines.append("- Python standard library only; no `uv` or project environment required.")
    return "\n".join(lines) + "\n"


def init_gitignore() -> None:
    upsert_marked(ROOT / ".gitignore", CRUISE_GITIGNORE_FRAGMENT, GITIGNORE_MARKER_START, GITIGNORE_MARKER_END)


def apply_setup() -> None:
    init_common_files()
    init_gitignore()


def cmd_setup(args: argparse.Namespace) -> None:
    if args.setup_cmd in {"check", "dry-run"}:
        print(setup_report(), end="")
        return
    if args.setup_cmd == "instructions":
        arg_path = Path(args.file)
        target = arg_path if arg_path.is_absolute() else ROOT / arg_path
        if target.name not in INSTRUCTION_FRAGMENTS:
            raise SystemExit(f"instructions target must be one of {sorted(INSTRUCTION_FRAGMENTS)}; got {target.name}")
        write_instructions(target)
        try:
            label = target.relative_to(ROOT)
        except ValueError:
            label = target
        print(f"Wrote Cruise protocol fragment to {label}.")
        return
    apply_setup()
    print("Applied Cruise setup.")
    print()
    print(setup_report(), end="")


def cmd_package(args: argparse.Namespace) -> None:
    if args.package_cmd == "sync":
        sync_package_skills()
        print("Synced installable Cruise skills under skills/.")


def cmd_init(args: argparse.Namespace) -> None:
    apply_setup()
    print("Initialized Cruise session protocol.")


def cmd_nudge(args: argparse.Namespace) -> None:
    path = CRUISE / "nudge.md"
    if args.nudge_cmd == "set":
        atomic_write(path, args.text.strip() + "\n")
        append_log(CRUISE / "nudges.log.md", "set", [args.text.strip()])
    elif args.nudge_cmd == "append":
        current = read_text(path).rstrip()
        updated = (current + "\n" if current else "") + args.text.strip() + "\n"
        atomic_write(path, updated)
        append_log(CRUISE / "nudges.log.md", "append", [args.text.strip()])
    elif args.nudge_cmd == "ack":
        current = read_text(path).strip()
        append_log(CRUISE / "nudges.log.md", "ack", [current or "(no active nudge)"])
        print("Acknowledged active nudge." if current else "No active nudge to acknowledge.")
    elif args.nudge_cmd == "clear":
        current = read_text(path).strip()
        atomic_write(path, "")
        append_log(CRUISE / "nudges.log.md", "clear", [current or "(no active nudge)"])
    elif args.nudge_cmd == "show":
        current = read_text(path).strip()
        print(current if current else "(no active nudge)")


def cmd_plan(args: argparse.Namespace) -> None:
    plan = read_text(CRUISE / "plan.md")
    if args.plan_cmd == "show":
        print(plan, end="" if plan.endswith("\n") else "\n")
        return
    if not plan.strip():
        raise SystemExit(".cruise/plan.md is missing or empty")
    print(".cruise/plan.md exists and is non-empty.")


def plan_md_warning() -> str | None:
    plan_path = CRUISE / "plan.md"
    if not plan_path.exists():
        return f"warning: {plan_path.relative_to(ROOT)} is missing; the handoff has no current slice to inherit."
    plan = read_text(plan_path).strip()
    if not plan:
        return f"warning: {plan_path.relative_to(ROOT)} is empty; the handoff has no current slice to inherit."
    objective = section_after_heading(plan, "Current objective")
    slice_section = section_after_heading(plan, "Current slice")
    stale = []
    if not objective or objective.startswith("(not set"):
        stale.append("Current objective")
    if not slice_section or slice_section.startswith("(not set"):
        stale.append("Current slice")
    if stale:
        return (
            f"warning: {plan_path.relative_to(ROOT)} still contains placeholder content "
            f"({' and '.join(stale)} unset). The handoff inherits this — update "
            f"`.cruise/plan.md` and rerun handoff before declaring done."
        )
    return None


def cmd_handoff(args: argparse.Namespace) -> None:
    session_path = write_session(commit_requested=args.commit)
    print(f"Wrote {session_path.relative_to(ROOT)}")
    print("Wrote .cruise/next.md, .cruise/sessions/latest.md, and HANDOFF.md")
    if args.commit:
        maybe_commit()
    else:
        print("No commit requested.")
    warning = plan_md_warning()
    if warning:
        print(warning)


def cmd_resume(_args: argparse.Namespace) -> None:
    cruise_paths = [CRUISE / "next.md", SESSIONS / "latest.md", CRUISE / "plan.md", CRUISE / "nudge.md"]
    optional_paths = [ROOT / candidate for candidate in PLANNING_DOC_CANDIDATES if (ROOT / candidate).exists()]
    for path in cruise_paths + optional_paths:
        print(f"\n--- {path.relative_to(ROOT)} ---")
        text = read_text(path).strip()
        print(text if text else "(empty)")


def autonomy_data() -> tuple[dict[str, str], str]:
    return parse_frontmatter(read_text(CRUISE / "autonomy.md"))


def parse_utc(value: str) -> datetime | None:
    if not value or value == "null":
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def autonomy_counts() -> tuple[int, int]:
    text = read_text(CRUISE / "autonomy.log.md")
    starts = list(re.finditer(r"^## \S+ started\b", text, flags=re.MULTILINE))
    if starts:
        text = text[starts[-1].end():]
    iterations = len(re.findall(r"checkpoint iteration\s+\d+", text))
    commits = len(re.findall(r"^- commit: (?!none$).+", text, flags=re.MULTILINE))
    return iterations, commits


def autonomy_stop(reason: str, run_handoff: bool = True) -> None:
    path = CRUISE / "autonomy.md"
    text = replace_frontmatter(read_text(path), {"status": "stopped", "updated": utc_stamp()})
    atomic_write(path, text)
    append_log(CRUISE / "autonomy.log.md", "stopped", [f"- reason: {reason}"])
    if run_handoff:
        write_session(commit_requested=False)


def check_autonomy_endpoints() -> str | None:
    data, _body = autonomy_data()
    if data.get("status") != "active":
        return "autonomy lease is not active"
    expires = parse_utc(data.get("expires_at", ""))
    if expires and now() >= expires:
        return "time-expired"
    iterations, commits = autonomy_counts()
    max_iterations = data.get("max_iterations")
    if max_iterations and max_iterations != "null" and iterations >= int(max_iterations):
        return "iteration-budget-hit"
    max_commits = data.get("max_commits")
    if max_commits and max_commits != "null" and commits >= int(max_commits):
        return "commit-budget-hit"
    nudge = read_text(CRUISE / "nudge.md").lower()
    if re.search(r"\bstop\b|\bpause\b|approval required", nudge):
        return "active nudge requested stop"
    return None


def cmd_autonomy(args: argparse.Namespace) -> None:
    if args.autonomy_cmd == "start":
        data, _ = autonomy_data()
        if data.get("status") == "active":
            raise SystemExit("An autonomy lease is already active; stop it before creating a new one.")
        expires = now() + timedelta(minutes=args.minutes)
        content = render(
            read_text(TEMPLATES / "autonomy.md") or AUTONOMY_TEMPLATE,
            {
                "created": utc_stamp(),
                "expires_at": expires.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
                "max_iterations": str(args.max_iterations),
                "max_commits": str(args.max_commits),
                "objective": args.objective,
                "acceptance_criteria": args.acceptance_criteria,
                "allowed_scope": args.allowed_scope,
                "out_of_scope": args.out_of_scope,
            },
        )
        atomic_write(CRUISE / "autonomy.md", content)
        append_log(CRUISE / "autonomy.log.md", "started", [f"- objective: {args.objective}", f"- expires_at: {expires.isoformat()}"])
        print("Started bounded-autonomy lease.")
    elif args.autonomy_cmd == "status":
        data, body = autonomy_data()
        iterations, commits = autonomy_counts()
        print(f"status: {data.get('status', 'unknown')}")
        print(f"expires_at: {data.get('expires_at', 'null')}")
        print(f"iterations: {iterations}/{data.get('max_iterations', 'null')}")
        print(f"commits: {commits}/{data.get('max_commits', 'null')}")
        objective = section_after_heading(body, "Objective")
        if objective:
            print(f"objective: {objective}")
    elif args.autonomy_cmd == "stop":
        autonomy_stop(args.reason)
        print(f"Stopped bounded-autonomy lease: {args.reason}")
    elif args.autonomy_cmd == "checkpoint":
        append_log(
            CRUISE / "autonomy.log.md",
            f"checkpoint iteration {args.iteration}",
            [
                f"- summary: {args.summary}",
                f"- validation: {args.validation}",
                f"- commit: {args.commit}",
                f"- continue: {args.continue_}",
            ],
        )
        if args.continue_.lower() != "true":
            autonomy_stop("checkpoint requested stop")
            print("Checkpoint recorded and autonomy stopped.")
        else:
            print("Checkpoint recorded.")
    elif args.autonomy_cmd == "run":
        reason = check_autonomy_endpoints()
        if reason:
            autonomy_stop(reason)
            raise SystemExit(f"Autonomy stopped: {reason}")
        data, body = autonomy_data()
        iterations, commits = autonomy_counts()
        print("Autonomy lease is active.")
        print(f"expires_at: {data.get('expires_at', 'null')}")
        print(f"iterations: {iterations}/{data.get('max_iterations', 'null')}")
        print(f"commits: {commits}/{data.get('max_commits', 'null')}")
        objective = section_after_heading(body, "Objective")
        if objective:
            print(f"objective: {objective}")
        print("Run the next bounded work slice in the current human-approved session, then call `autonomy checkpoint`.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cruise_session.py")
    sub = parser.add_subparsers(dest="cmd", required=True)

    init = sub.add_parser("init")
    init.set_defaults(func=cmd_init)

    setup = sub.add_parser("cruise-setup")
    setup_sub = setup.add_subparsers(dest="setup_cmd", required=True)
    for name in ["check", "dry-run", "apply"]:
        item = setup_sub.add_parser(name)
        item.set_defaults(func=cmd_setup)
    instructions = setup_sub.add_parser("instructions")
    instructions.add_argument("file", help="AGENTS.md or CLAUDE.md (path relative to repo root)")
    instructions.set_defaults(func=cmd_setup)

    package = sub.add_parser("package")
    package_sub = package.add_subparsers(dest="package_cmd", required=True)
    sync = package_sub.add_parser("sync")
    sync.set_defaults(func=cmd_package)

    nudge = sub.add_parser("nudge")
    nudge_sub = nudge.add_subparsers(dest="nudge_cmd", required=True)
    for name in ["set", "append"]:
        item = nudge_sub.add_parser(name)
        item.add_argument("text")
        item.set_defaults(func=cmd_nudge)
    for name in ["ack", "clear", "show"]:
        item = nudge_sub.add_parser(name)
        item.set_defaults(func=cmd_nudge)

    plan = sub.add_parser("plan")
    plan_sub = plan.add_subparsers(dest="plan_cmd", required=True)
    for name in ["show", "check"]:
        item = plan_sub.add_parser(name)
        item.set_defaults(func=cmd_plan)

    handoff = sub.add_parser("handoff")
    group = handoff.add_mutually_exclusive_group(required=True)
    group.add_argument("--no-commit", action="store_true")
    group.add_argument("--commit", action="store_true")
    handoff.set_defaults(func=cmd_handoff)

    resume = sub.add_parser("resume")
    resume.set_defaults(func=cmd_resume)

    autonomy = sub.add_parser("autonomy")
    autonomy_sub = autonomy.add_subparsers(dest="autonomy_cmd", required=True)
    start = autonomy_sub.add_parser("start")
    start.add_argument("--objective", required=True)
    start.add_argument("--acceptance-criteria", required=True)
    start.add_argument("--allowed-scope", required=True)
    start.add_argument("--out-of-scope", required=True)
    start.add_argument("--minutes", required=True, type=int)
    start.add_argument("--max-iterations", required=True, type=int)
    start.add_argument("--max-commits", required=True, type=int)
    start.set_defaults(func=cmd_autonomy)
    status = autonomy_sub.add_parser("status")
    status.set_defaults(func=cmd_autonomy)
    stop = autonomy_sub.add_parser("stop")
    stop.add_argument("--reason", required=True)
    stop.set_defaults(func=cmd_autonomy)
    checkpoint = autonomy_sub.add_parser("checkpoint")
    checkpoint.add_argument("--iteration", required=True, type=int)
    checkpoint.add_argument("--summary", required=True)
    checkpoint.add_argument("--validation", required=True)
    checkpoint.add_argument("--commit", required=True)
    checkpoint.add_argument("--continue", dest="continue_", required=True, choices=["true", "false"])
    checkpoint.set_defaults(func=cmd_autonomy)
    run = autonomy_sub.add_parser("run")
    run.set_defaults(func=cmd_autonomy)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
