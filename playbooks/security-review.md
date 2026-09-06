---
playbook: security-review
goal_patterns:
  - is this safe to expose
  - audit security before launch
  - pentest and compliance
  - posture and vulnerability scan
---

# Playbook: Security Review

Audit architecture, dependencies, cloud perimeter, and compliance controls before public exposure.

| # | Stage | Groups | Deliverable | Parallel |
|---|---|---|---|---|
| 1 | Scout reality | scout | business-brief.md | no |
| 2 | Technical security & penetration scan | developer:Security | vulnerability-audit.md | yes |
| 3 | Regulatory & privacy compliance | legal:Compliance | compliance-matrix.md | yes |
| 4 | Legal documents & user agreements | legal:Contracts | legal-risk-report.md | no |
| 5 | Quality verification | verifier | verification.md | no |
