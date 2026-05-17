from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SOURCE_ROOT = Path(__file__).resolve().parents[1]
SOURCE_SCRIPT = SOURCE_ROOT / ".cruise" / "scripts" / "cruise_session.py"


class CruiseSessionTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        script = self.root / ".cruise" / "scripts" / "cruise_session.py"
        script.parent.mkdir(parents=True)
        shutil.copy2(SOURCE_SCRIPT, script)
        shutil.copytree(SOURCE_ROOT / "skills", self.root / "skills")
        self.script = script

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(self.script), *args],
            cwd=self.root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )

    def test_setup_apply_creates_protocol_without_adapters(self) -> None:
        result = self.run_cli("setup", "apply")

        self.assertIn("Applied Cruise setup.", result.stdout)
        self.assertTrue((self.root / ".cruise" / "protocol.md").exists())
        self.assertTrue((self.root / ".cruise" / "config.json").exists())
        self.assertTrue((self.root / ".cruise" / "spec.md").exists())
        self.assertIn("provisional decisions", (self.root / ".cruise" / "protocol.md").read_text(encoding="utf-8"))
        self.assertIn("Read `.cruise/protocol.md`", (self.root / "AGENTS.md").read_text(encoding="utf-8"))
        self.assertIn("Read `.cruise/protocol.md`", (self.root / "CLAUDE.md").read_text(encoding="utf-8"))
        self.assertIn("repo-local adapter skill copies are not generated", result.stdout)
        self.assertFalse((self.root / ".agents").exists())
        self.assertFalse((self.root / ".claude").exists())
        self.assertFalse((self.root / ".opencode").exists())
        self.assertFalse((self.root / ".codex").exists())
        self.assertIn("Provisional decisions", (self.root / ".cruise" / "spec.md").read_text(encoding="utf-8"))
        old_name = "ai" + "_session.py"
        self.assertFalse((self.root / ".cruise" / "scripts" / old_name).exists())
        removed_dir = "la" + "nes"
        self.assertFalse((self.root / ".cruise" / removed_dir).exists())

    def test_package_sync_creates_neutral_installable_skills(self) -> None:
        result = self.run_cli("package", "sync")

        self.assertIn("Synced installable Cruise skills", result.stdout)
        self.assertTrue((self.root / "skills" / "setup" / "SKILL.md").exists())
        self.assertTrue((self.root / "skills" / "autostart" / "SKILL.md").exists())
        self.assertTrue((self.root / "skills" / "autorun" / "SKILL.md").exists())
        self.assertTrue((self.root / "skills" / "autostop" / "SKILL.md").exists())
        self.assertFalse((self.root / "skills" / "kickoff" / "SKILL.md").exists())
        self.assertTrue((self.root / "skills" / "setup" / "scripts" / "cruise_session.py").exists())
        self.assertTrue((self.root / "skills" / "diagnose" / "scripts" / "hitl-loop.template.sh").exists())
        setup_text = (self.root / "skills" / "setup" / "SKILL.md").read_text(encoding="utf-8")
        autostart_text = (self.root / "skills" / "autostart" / "SKILL.md").read_text(encoding="utf-8")
        autorun_text = (self.root / "skills" / "autorun" / "SKILL.md").read_text(encoding="utf-8")
        autostop_text = (self.root / "skills" / "autostop" / "SKILL.md").read_text(encoding="utf-8")
        handoff_text = (self.root / "skills" / "handoff" / "SKILL.md").read_text(encoding="utf-8")
        zoom_out_text = (self.root / "skills" / "zoom-out" / "SKILL.md").read_text(encoding="utf-8")
        shape_text = (self.root / "skills" / "shape" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("bundled `scripts/cruise_session.py`", setup_text)
        self.assertIn("name: autostart", autostart_text)
        self.assertIn("acceptance criteria", autostart_text)
        for skill_text in [setup_text, autostart_text, autorun_text, autostop_text, handoff_text, zoom_out_text]:
            self.assertIn("disable-model-invocation: true", skill_text)
        self.assertIn("A good handoff captures", handoff_text)
        self.assertIn("Go up a layer of abstraction.", zoom_out_text)
        self.assertNotIn("allow_implicit_invocation", shape_text)

    def test_nudge_and_handoff_no_commit(self) -> None:
        self.run_cli("setup", "apply")
        self.run_cli("nudge", "set", "Move to seccomp after this slice")
        show = self.run_cli("nudge", "show")
        self.assertEqual(show.stdout.strip(), "Move to seccomp after this slice")

        handoff = self.run_cli("handoff", "--no-commit")
        self.assertIn("No commit requested.", handoff.stdout)
        self.assertTrue((self.root / ".cruise" / "next.md").exists())
        self.assertTrue((self.root / ".cruise" / "sessions" / "latest.md").exists())
        self.assertIn("## Pending artifacts", (self.root / "HANDOFF.md").read_text(encoding="utf-8"))
        self.assertIn("## Provisional decisions", (self.root / "HANDOFF.md").read_text(encoding="utf-8"))

    def test_setup_preserves_claude_symlink_to_agents(self) -> None:
        agents = self.root / "AGENTS.md"
        agents.write_text("# Existing Instructions\n\nKeep this.\n", encoding="utf-8")
        (self.root / "CLAUDE.md").symlink_to("AGENTS.md")

        self.run_cli("setup", "apply")

        self.assertTrue((self.root / "CLAUDE.md").is_symlink())
        text = agents.read_text(encoding="utf-8")
        self.assertIn("Keep this.", text)
        self.assertEqual(text.count("<!-- cruise-session-protocol:start -->"), 1)
        self.assertIn("Read `.cruise/protocol.md`", text)

    def test_setup_check_reports_without_applying(self) -> None:
        result = self.run_cli("setup", "check")

        self.assertIn("# Cruise Setup Report", result.stdout)
        self.assertIn(".cruise/protocol.md: missing", result.stdout)
        self.assertFalse((self.root / "AGENTS.md").exists())


if __name__ == "__main__":
    unittest.main()
