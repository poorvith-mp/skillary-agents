# skillary-agents

> Install once, pull any of 277 verified skills on demand, and turn any of 300+ AI models into a domain expert. Standalone expert router and multi-agent orchestrator for Claude Code, Google Antigravity, Gemini, Codex, Cursor, and open-source models.

## What it is

You install `skillary-agents` once. When you give your model a prompt or goal (like fixing a backend bug, redesigning a UI component, writing a Unity shader, or auditing authentication), `skillary-agents` maps your prompt to one of **11 Domain Expert Personas**, pulls only the 2-4 required `SKILL.md` files from the 277-skill Skillary `v4.1.0` catalog on demand, and guides your model through concrete execution steps.

Whether you run **Gemini 4 Argon**, **Gemini 3.8 Flash**, **Claude Opus 5.5**, **Fable 5.1**, **GPT-6 Astra**, or any of **300+ open-source / OpenRouter models**, the router emits a portable action guide containing the exact skill checklists your task needs.

## Quickstart (On-Demand Expert Routing & Skill Pull)

Route any prompt, pull the matched `SKILL.md` files into `.agents/skills/`, and generate a self-contained model guide:

```bash
python scripts/skillary_agent.py \
  --goal "fix a failing unit test and memory leak in my Python backend" \
  --model "gemini-4-argon" \
  --pull \
  --emit .skillary/active-expert-guide.md
```

Inspect routing and matched skills as JSON without writing files:

```bash
python scripts/skillary_agent.py \
  --goal "redesign dashboard UI and fix WCAG contrast" \
  --model "opus-5.5" \
  --dry-run \
  --json
```

## Architecture

```text
skillary-agents/
├── AGENTS.md              # protocol + single-model & crew execution loop
├── README.md
├── CHANGELOG.md
├── LICENSE                # MIT
├── VERSION                # 5.0.0
├── capabilities.md        # host vocabulary + 300+ model routing matrix
├── experts/
│   └── _index.md          # 11 domain expert personas across all categories
├── roles/                 # crew role templates — no skill slugs hardcoded
│   ├── scout.md
│   ├── planner.md
│   ├── worker.md
│   ├── verifier.md
│   ├── security-auditor.md
│   └── shipper.md
├── playbooks/             # priors for multi-stage goals
│   ├── _index.md
│   ├── launch-business.md
│   ├── fundraise.md
│   ├── ship-feature.md
│   ├── codebase-rescue.md
│   ├── content-engine.md
│   ├── hire-a-team.md
│   ├── security-review.md
│   └── sell-a-thing.md
├── index/
│   ├── experts.json       # 11 expert definitions, intent keywords, action steps
│   ├── skills.json        # 277 skills mirrored from skillary v4.1.0
│   └── repos.json         # 12 category repos -> GitHub URLs
├── scripts/
│   ├── skillary_agent.py  # zero-dependency prompt router & SKILL.md puller
│   ├── sync_index.py      # sync index/skills.json from skillary
│   └── validate.py        # CI gate for roles, playbooks, and experts
└── tests/
    └── test_skillary_agent.py
```

## 11 Domain Expert Personas

| Expert ID | Expert Persona | Categories Spanned |
|---|---|---|
| `fullstack-bugfix-dev` | Full-Stack & Bug-Fix Developer | `developer` |
| `ux-ui-design-engineer` | UX/UI & Design Systems Engineer | `design`, `developer` |
| `game-developer` | Game Developer | `gamedev` |
| `ai-agent-architect` | AI & Agent Architect | `agents`, `developer` |
| `security-devsecops-auditor` | Security & DevSecOps Auditor | `developer`, `legal` |
| `growth-distribution-strategist` | Growth & Organic Distribution Strategist | `marketing` |
| `technical-longform-writer` | Technical & Long-Form Writer | `writing` |
| `product-operations-strategist` | Product & Operations Strategist | `business` |
| `sales-revops-specialist` | Sales & RevOps Specialist | `sales`, `marketing` |
| `finance-economics-analyst` | Finance & Unit Economics Analyst | `finance`, `business` |
| `legal-privacy-learning-advisor` | Legal, Privacy & Learning Advisor | `legal`, `education`, `personal` |

## Supported Agents & Models

| Host / Model Family | Status |
|---|---|
| Claude Code (Opus 5.5, Sonnet) | ✅ Full crew dispatch + native `.claude/skills/` pull |
| Google Antigravity (Gemini 4 Argon, Gemini 3.8 Flash) | ✅ Full sub-agent dispatch + `.agents/skills/` pull |
| OpenAI Codex CLI / Cursor (GPT-6 Astra, Fable 5.1) | ✅ Worktree dispatch + `.agents/skills/` pull |
| Gemini CLI & Gemini App | ✅ Native skills import & CLI invocation |
| Cline & Roo Code | ✅ Native skill folder & `.skillary/active-expert-guide.md` |
| 300+ OpenRouter, Ollama & Local OSS Models | ✅ Universal action guide via `--emit .skillary/active-expert-guide.md` |

## Protocol Rules That Never Bend

1. **You are the parent.** You dispatch. Children never dispatch. Depth is 1.
2. **Nothing is written to the user's filesystem before they approve it** — installing skills included.
3. **Nothing is deployed, published, sent or posted without a separate approval at the moment it happens.**
4. **Never silently degrade.** Skipped agent, absent skill, timed-out child, capability this host lacks — all of it goes in the closing report.
5. **At most 3 children running at once.**
6. **Every child gets a deadline.** Default 300 seconds.
7. **Read-only unless the job needs to write.**

## License

MIT © [Poorvith M P](https://github.com/poorvith-mp)
