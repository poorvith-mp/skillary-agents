# Changelog

All notable changes to `skillary-agents` are documented in this file.

## v5.0.0 — October 2026

Turns `skillary-agents` into an executable, zero-dependency domain expert router and on-demand `SKILL.md` puller across all 277 verified Skillary skills (`v4.1.0`) and 300+ frontier or open-source models.

### Added
- **11 Domain Expert Personas (`index/experts.json`, `experts/_index.md`)**:
  - Added `fullstack-bugfix-dev`, `ux-ui-design-engineer`, `game-developer`, `ai-agent-architect`, `security-devsecops-auditor`, `growth-distribution-strategist`, `technical-longform-writer`, `product-operations-strategist`, `sales-revops-specialist`, `finance-economics-analyst`, and `legal-privacy-learning-advisor` mapped across the 12 Skillary `skills-*` repositories.
- **Zero-Dependency Prompt Router & On-Demand Puller (`scripts/skillary_agent.py`)**:
  - Routes any user prompt or goal (`--goal`) to the best domain expert and top matching `SKILL.md` files from `index/skills.json`.
  - Automatically detects and enforces `skillary.lock` when present in the project root, `~/.claude/`, or `~/.gemini/`.
  - Pulls only the required `SKILL.md` files on demand (`--pull`) from local sibling checkouts or over HTTPS from `poorvith-mp/skills-*` (`v4.1.0` tag with `main` fallback) and computes SHA-256 checksums.
  - Emits a self-contained, model-agnostic action guide (`--emit .skillary/active-expert-guide.md`) containing the expert persona, mandatory action steps, and pulled `SKILL.md` bodies.
- **Universal 300+ Model Support (`AGENTS.md`, `capabilities.md`)**:
  - Added single-model and multi-agent routing guidance for Gemini 4 Argon (`gemini-4-argon`), Gemini 3.8 Flash (`gemini-3.8-flash`), Claude Opus 5.5 (`opus-5.5`), Fable 5.1 (`fable-5.1`), GPT-6 Astra (`gpt-6-astra`), and 300+ OpenRouter / Ollama / local open-source models.
- **Validator & Unit Test Suite (`scripts/validate.py`, `tests/test_skillary_agent.py`)**:
  - Extended `validate.py` to verify all 11 expert definitions against `index/skills.json` and assert zero hardcoded skill slugs across `experts/*.md`.
  - Added `tests/test_skillary_agent.py` covering all 11 domain routing paths, `skillary.lock` filtering, path-traversal protection, and on-demand skill pulling.

## v4.1.0 — October 2026

- Added Gemini App, Gemini CLI, Google Antigravity, Cline, and Roo Code support in `AGENTS.md`, `capabilities.md`, and `README.md`.
- Added `skillary.lock` preference rule across `scout`, `planner`, and `worker` role contracts.

## v3.0.0 — September 2026

- Initial standalone release of `skillary-agents` with 6 zero-slug role contracts (`scout`, `planner`, `worker`, `verifier`, `security-auditor`, `shipper`) and 8 cross-category playbooks.
