# Domain Expert Personas (11 Categories)

When a user installs `skillary-agents` and gives a direct prompt or goal, the router maps their intent to one of 11 domain expert personas defined in `index/experts.json`. Each expert spans specific category repositories and functional groups in `index/skills.json`, pulling only the required `SKILL.md` files on demand.

## Expert Persona Catalog

| Expert ID | Expert Title | Categories Spanned | Functional Groups |
|---|---|---|---|
| `fullstack-bugfix-dev` | Full-Stack & Bug-Fix Developer | `developer` | `Build`, `Quality`, `Migrate and modernise`, `Ship and run`, `Understand and design` |
| `ux-ui-design-engineer` | UX/UI & Design Systems Engineer | `design`, `developer` | `Interface`, `Design system`, `Implementation`, `Brand`, `Direction`, `Research and evaluation`, `Domain-specific` |
| `game-developer` | Game Developer | `gamedev` | `Engineering`, `Unity`, `Unreal`, `3D assets`, `Art and audio`, `Craft`, `Plan` |
| `ai-agent-architect` | AI & Agent Architect | `agents`, `developer` | `Agent design`, `Prompts and skills`, `Retrieval`, `Tooling agents call`, `Workflow automation`, `Outputs`, `Data and AI` |
| `security-devsecops-auditor` | Security & DevSecOps Auditor | `developer`, `legal` | `Security`, `Repo hygiene`, `Compliance` |
| `growth-distribution-strategist` | Growth & Organic Distribution Strategist | `marketing` | `Distribution`, `Search and AI discovery`, `Website conversion`, `Content`, `Foundation`, `Measurement`, `Assets`, `Earned and partnerships`, `Lifecycle`, `Offer and money`, `Operating layer`, `Paid`, `Platform and naming` |
| `technical-longform-writer` | Technical & Long-Form Writer | `writing` | `Documents`, `Long form`, `Voice and quality`, `Research support`, `Repurposing and translation`, `Workplace` |
| `product-operations-strategist` | Product & Operations Strategist | `business` | `Product and delivery`, `Strategy`, `Operations`, `People`, `Reporting` |
| `sales-revops-specialist` | Sales & RevOps Specialist | `sales`, `marketing` | `Pipeline`, `Enablement`, `Bidding`, `Post-sale`, `Sales handoff` |
| `finance-economics-analyst` | Finance & Unit Economics Analyst | `finance`, `business` | `Modelling`, `Accounting`, `Investing`, `Tax`, `Fundraising and board` |
| `legal-privacy-learning-advisor` | Legal, Privacy & Learning Advisor | `legal`, `education`, `personal` | `Contracts`, `Product and website`, `Intellectual property`, `Company`, `Compliance`, `Learning`, `Teaching and planning`, `Assessment`, `Research`, `Knowledge and productivity`, `Career`, `Habits and health`, `Identity`, `Life admin`, `Hobby` |

## How Expert Selection Works

1. **Intent Scoring**: User prompt tokens are matched against each expert's `intent_keywords` and functional `groups`.
2. **Scoped Skill Resolution**: Once the primary expert persona is selected, candidate skills in `index/skills.json` belonging to that expert's categories and groups receive a priority boost while cross-category matches remain eligible.
3. **Lockfile Discipline**: If `skillary.lock` is present in the workspace, `~/.claude/`, or `~/.gemini/`, selection is strictly filtered to locked skill slugs.
4. **Action Execution**: The matched `SKILL.md` files are pulled on demand and combined with the expert's `default_action_steps` to guide any model through execution.
