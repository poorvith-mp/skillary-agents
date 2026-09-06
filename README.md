# skillary-agents

> A company of experts you install once. Standalone multi-agent orchestration for Claude Code, Google Antigravity, and Codex / Cursor.

## What it is

The user installs `skillary-agents` into their coding agent. They state a goal in plain language. It inspects their business, determines which skills the job needs across every category, installs only those skill folders, writes the crew for that specific engagement, dispatches it from planning through to shipping, and hands back finished work.

**It ships no skills.** It ships a protocol, role templates, playbooks, and an index.

## Architecture

```text
skillary-agents/
├── AGENTS.md              # the protocol — every host reads this first
├── README.md
├── LICENSE                # MIT
├── VERSION                # 4.0.0
├── capabilities.md        # host-neutral tool vocabulary + per-host map
├── roles/                 # role templates — no skill names, ever
│   ├── scout.md
│   ├── planner.md
│   ├── worker.md
│   ├── verifier.md
│   ├── security-auditor.md
│   └── shipper.md
├── playbooks/             # priors for common goals, referencing groups not slugs
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
│   ├── skills.json        # mirrored from skillary/dist
│   └── repos.json         # repo -> install URL
└── scripts/
    ├── sync_index.py      # pull the index, fail if a playbook group is gone
    └── validate.py        # CI gate
```

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
