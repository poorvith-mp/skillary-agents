"""Unit tests for the skillary-agents v5.0.0 expert router and on-demand SKILL.md puller."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import skillary_agent  # noqa: E402


class TestSkillaryAgentRouter(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skills = json.loads((ROOT / "index" / "skills.json").read_text(encoding="utf-8"))
        cls.experts = json.loads((ROOT / "index" / "experts.json").read_text(encoding="utf-8"))
        cls.repos = json.loads((ROOT / "index" / "repos.json").read_text(encoding="utf-8"))

    def test_11_experts_loaded(self) -> None:
        self.assertEqual(len(self.experts), 11)

    def test_prompt_to_expert_routing_across_domains(self) -> None:
        cases = [
            ("Fix a failing unit test and memory leak in Python backend API", "fullstack-bugfix-dev"),
            ("Redesign the mobile UI layout and fix WCAG accessibility contrast", "ux-ui-design-engineer"),
            ("Optimize a Unity 3D HLSL shader and collision raycast framerate", "game-developer"),
            ("Build an MCP tool server and RAG vector retrieval workflow for an LLM agent", "ai-agent-architect"),
            ("Audit OAuth JWT authentication and prevent SQL injection or secret leaks", "security-devsecops-auditor"),
            ("Plan an organic SEO and AEO product launch funnel with high conversion", "growth-distribution-strategist"),
            ("Write technical documentation, a README tutorial, and a post-mortem article", "technical-longform-writer"),
            ("Draft a product roadmap PRD and set quarterly OKR operations", "product-operations-strategist"),
            ("Build an enterprise sales outbound discovery and RFP bidding pipeline", "sales-revops-specialist"),
            ("Model SaaS unit economics, LTV/CAC, burn rate, and seed fundraise runway", "finance-economics-analyst"),
            ("Review a SaaS privacy policy, NDA contract, and BTech study curriculum", "legal-privacy-learning-advisor"),
        ]
        for prompt, expected_expert_id in cases:
            with self.subTest(prompt=prompt):
                expert = skillary_agent.select_expert(prompt, self.experts)
                self.assertEqual(expert["id"], expected_expert_id)

    def test_rank_skills_respects_lockfile_and_category(self) -> None:
        expert = skillary_agent.select_expert("fix accessibility and UI design", self.experts)
        locked = {"accessibility-fix", "api-design"}
        matched = skillary_agent.rank_skills(
            "fix accessibility and UI design",
            expert,
            self.skills,
            limit=4,
            locked_slugs=locked,
        )
        slugs = [m["slug"] for m in matched]
        self.assertIn("accessibility-fix", slugs)
        self.assertTrue(set(slugs).issubset(locked))

    def test_fetch_skill_rejects_traversal_and_unknown_repo(self) -> None:
        with self.assertRaises(ValueError):
            skillary_agent.fetch_skill_body(
                {"slug": "../etc/passwd", "repo": "skills-developer"},
                self.repos,
                ROOT,
            )
        with self.assertRaises(ValueError):
            skillary_agent.fetch_skill_body(
                {"slug": "api-design", "repo": "skills-evil"},
                self.repos,
                ROOT,
            )

    def test_pull_and_emit_universal_model_guide(self) -> None:
        models = ["gemini-4-argon", "gemini-3.8-flash", "opus-5.5", "fable-5.1", "gpt-6-astra", "openrouter/qwen-3"]
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            install_dir = tmp_path / "skills"
            guide_path = tmp_path / "active-expert-guide.md"

            rc = skillary_agent.main(
                [
                    "--goal",
                    "fix a failing backend test and API bug",
                    "--model",
                    models[0],
                    "--limit",
                    "2",
                    "--pull",
                    "--install-dir",
                    str(install_dir),
                    "--emit",
                    str(guide_path),
                    "--json",
                ]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(guide_path.exists())
            guide_text = guide_path.read_text(encoding="utf-8")
            self.assertIn("gemini-4-argon", guide_text)
            self.assertIn("Full-Stack & Bug-Fix Developer", guide_text)
            self.assertIn("## 3. Mounted Skill Instructions", guide_text)
            installed_files = list(install_dir.glob("*/SKILL.md"))
            self.assertEqual(len(installed_files), 2)


if __name__ == "__main__":
    unittest.main()
