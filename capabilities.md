# Capabilities and Host Vocabulary

Roles declare capabilities. This maps them to host primitives across Claude Code, Antigravity, and Codex / Cursor / CLI.

| Capability | Claude Code | Antigravity | Gemini CLI | Codex / CLI |
|---|---|---|---|---|
| `read.file` | `Read` | `view_file` | `read_file` | `cat`, `sed -n` |
| `search.code` | `Grep`, `Glob` | `grep_search`, `find_by_name` | `grep_search`, `glob` | `rg`, `find` |
| `read.web` | `WebFetch` | `read_url_content` | `read_url` | `curl` |
| `search.web` | `WebSearch` | `search_web` | `search_web` | provider-specific |
| `write.file` | `Write` | `write_to_file` | `write_file` | heredoc |
| `edit.file` | `Edit` | `replace_file_content` | `replace` | `sed -i`, patch |
| `exec.shell` | `Bash` | `run_command` | `run_shell_command` | shell |
| `dispatch` | `Task` | `invoke_subagent` | `invoke_agent` | `git worktree` + CLI worker |

## Skill Install Paths

Detected per host:

| Host | Project | Personal |
|---|---|---|
| Claude Code | `.claude/skills/` | `~/.claude/skills/` |
| Antigravity | `.agents/skills/` | — |
| Gemini CLI | `.gemini/skills/` or `.agents/skills/` | `~/.gemini/skills/` |
| Gemini App | — (cloud-based) | Settings → Skills (upload SKILL.md or .skill bundle) |
| Codex / Cursor | `.agents/skills/` | `~/.cursor/skills/`, `~/.codex/skills/` |
| Cline | `.cline/skills/` | `~/.cline/skills/` |
| Roo Code | `.roo/rules/` | `~/.roo/rules/` |

A missing capability means **skip the agent and report it**, never a degraded substitute.

## Dispatch per Host

- **Claude Code**: `Task`, one call per specialist, backgrounded so they run concurrently. The child's prompt carries its mounted skill bodies and its deliverable contract, and tells it that it may not dispatch further.
- **Antigravity**: `invoke_subagent` with a `Subagents` array carrying `Role`, `TypeName`, `Prompt`, `Workspace`. Read-only roles take `inherit`; workers that mutate take `branch`.
- **Codex / Cursor / terminal**: An isolated worktree per mutating worker:
  ```bash
  git worktree add -b skillary/worker-1 .worktrees/worker-1
  codex exec --workspace .worktrees/worker-1 "<child prompt>"
  git worktree remove --force .worktrees/worker-1
  ```
  Read-only workers need no worktree.
- **Gemini CLI**: `invoke_agent` with `agent_name: "generalist"` (or `@generalist` in chat). The child's prompt carries its mounted skill bodies. Read-only roles skip workspace isolation.
- **Gemini App**: No dispatch capability — skills are used directly in conversations, not in multi-agent orchestration.
