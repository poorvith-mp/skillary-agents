---
playbook: codebase-rescue
goal_patterns:
  - inherited a mess
  - rescue codebase
  - untangle legacy code
  - technical debt cleanup
---

# Playbook: Codebase Rescue

Map, stabilize, and remediate legacy or tangled software projects safely.

| # | Stage | Groups | Deliverable | Parallel |
|---|---|---|---|---|
| 1 | Scout reality | scout | business-brief.md | no |
| 2 | Architecture & dependency mapping | developer:Understand and design | architecture-audit.md | no |
| 3 | Regression safety net & test harness | developer:Quality | safety-harness-report.md | yes |
| 4 | Strangler migration & refactoring plan | developer:Migrate and modernise | migration-plan.md | yes |
| 5 | Repository docs & operational hygiene | developer:Repo hygiene | maintenance-guide.md | no |
| 6 | Quality verification | verifier | verification.md | no |
