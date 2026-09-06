# Capabilities and Host Vocabulary

Roles declare capabilities. This maps them to host primitives across Claude Code, Antigravity, and Codex / Cursor / CLI.

| Capability | Claude Code | Antigravity | Codex / CLI |
|---|---|---|---|
| `read.file` | `Read` | `view_file` | `cat`, `sed -n` |
| `search.code` | `Grep`, `Glob` | `grep_search`, `find_by_name` | `rg`, `find` |
| `read.web` | `WebFetch` | `read_url_content` | `curl` |
| `search.web` | `WebSearch` | `search_web` | provider-specific |
| `write.file` | `Write` | `write_to_file` | heredoc |
| `edit.file` | `Edit` | `replace_file_content` | `sed -i`, patch |
| `exec.shell` | `Bash` | `run_command` | shell |
| `dispatch` | `Task` | `invoke_subagent` | `git worktree` + CLI worker |

## Skill Install Paths

Detected per host:

| Host | Project | Personal |
|---|---|---|
| Claude Code | `.claude/skills/` | `~/.claude/skills/` |
| Antigravity | `.agents/skills/` | — |
| Codex / Cursor / Gemini CLI | `.agents/skills/` | `~/.cursor/skills/`, `~/.gemini/skills/` |

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
