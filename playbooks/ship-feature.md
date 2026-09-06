---
playbook: ship-feature
goal_patterns:
  - ship feature
  - build and deploy feature
  - implement feature
  - deliver engineering spec
---

# Playbook: Ship Feature

Engineer and safely deploy a new feature from system architecture to production cutover.

| # | Stage | Groups | Deliverable | Parallel |
|---|---|---|---|---|
| 1 | Scout reality | scout | business-brief.md | no |
| 2 | Contract & system design | developer:Understand and design | technical-spec.md | no |
| 3 | Execution plan & milestones | developer:Plan | implementation-plan.md | no |
| 4 | Core implementation | developer:Build | feature-implementation.md | no |
| 5 | Test suites & verification | developer:Quality | test-report.md | yes |
| 6 | Security review | developer:Security | security-report.md | yes |
| 7 | Deployment & release | developer:Ship and run | deploy-changelog.md | no |
