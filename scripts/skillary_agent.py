"""Zero-dependency expert router and on-demand SKILL.md puller for skillary-agents.

Routes any user prompt or goal to one of 11 domain expert personas across the 277
Skillary skills (v4.1.0), pulls only the required SKILL.md files on demand, and
emits a model-agnostic action guide for any frontier or open-source model.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "has", "have",
    "how", "i", "in", "into", "is", "it", "my", "need", "of", "on", "or", "our",
    "please", "should", "so", "some", "that", "the", "their", "this", "to", "us",
    "use", "using", "want", "we", "what", "when", "where", "which", "with", "you", "your",
}

INTENT_SYNONYMS: dict[str, list[str]] = {
    "bug": ["debug", "fix", "error", "quality", "test", "incident", "root-cause", "triage"],
    "fix": ["bug", "debug", "refactor", "quality", "test", "remediate"],
    "crash": ["incident", "debug", "error", "observability", "reliability"],
    "leak": ["memory", "performance", "profiling", "security", "secret"],
    "ui": ["interface", "design", "frontend", "component", "accessibility", "css", "layout"],
    "ux": ["interface", "design", "research", "usability", "onboarding", "accessibility"],
    "design": ["interface", "design-system", "brand", "typography", "component", "ui"],
    "game": ["gamedev", "unity", "unreal", "shader", "physics", "3d", "frame"],
    "unity": ["gamedev", "shader", "csharp", "physics", "3d"],
    "unreal": ["gamedev", "blueprint", "shader", "3d"],
    "security": ["vulnerability", "audit", "authentication", "encryption", "compliance", "threat"],
    "agent": ["llm", "prompt", "rag", "mcp", "orchestrator", "retrieval", "workflow"],
    "launch": ["marketing", "distribution", "positioning", "conversion", "seo", "growth"],
}

SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def _stem(word: str) -> str:
    if len(word) > 5 and word.endswith("ing"):
        return word[:-3]
    if len(word) > 4 and word.endswith("ed"):
        return word[:-2]
    if len(word) > 4 and word.endswith("es"):
        return word[:-2]
    if len(word) > 4 and word.endswith("s") and not word.endswith("ss"):
        return word[:-1]
    return word


def tokenize(text: str) -> list[str]:
    raw_tokens = re.findall(r"[a-z0-9]+", text.lower())
    tokens: list[str] = []
    for tok in raw_tokens:
        if tok in STOPWORDS or len(tok) < 2:
            continue
        tokens.append(tok)
        stemmed = _stem(tok)
        if stemmed != tok and len(stemmed) >= 2:
            tokens.append(stemmed)
    return tokens


def expand_tokens(tokens: list[str]) -> set[str]:
    expanded = set(tokens)
    for tok in list(expanded):
        for syn in INTENT_SYNONYMS.get(tok, []):
            expanded.update(tokenize(syn))
    return expanded


def find_lockfile(explicit_lock: Path | None = None) -> Path | None:
    if explicit_lock:
        return explicit_lock if explicit_lock.exists() else None
    candidates = [
        Path.cwd() / "skillary.lock",
        Path.home() / ".claude" / "skillary.lock",
        Path.home() / ".gemini" / "skillary.lock",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def load_locked_slugs(lock_path: Path | None) -> set[str] | None:
    if not lock_path or not lock_path.exists():
        return None
    data = json.loads(lock_path.read_text(encoding="utf-8"))
    skills_obj = data.get("skills", {})
    if isinstance(skills_obj, dict):
        return set(skills_obj.keys())
    return set()


def select_expert(goal: str, experts: list[dict[str, Any]]) -> dict[str, Any]:
    tokens = set(tokenize(goal))
    expanded = expand_tokens(list(tokens))
    best_expert = experts[0]
    best_score = -1

    for expert in experts:
        score = 0
        keywords = {k.lower() for k in expert.get("intent_keywords", [])}
        keyword_stems = {_stem(k) for k in keywords}
        for tok in tokens:
            if tok in keywords or _stem(tok) in keyword_stems:
                score += 4
        for tok in expanded - tokens:
            if tok in keywords or _stem(tok) in keyword_stems:
                score += 2
        for cat in expert.get("categories", []):
            if cat.lower() in expanded:
                score += 3
        for grp in expert.get("groups", []):
            grp_tokens = set(tokenize(grp))
            score += len(tokens & grp_tokens) * 2
        if score > best_score:
            best_score = score
            best_expert = expert

    return best_expert


def rank_skills(
    goal: str,
    expert: dict[str, Any],
    skills: list[dict[str, Any]],
    limit: int = 4,
    category: str | None = None,
    locked_slugs: set[str] | None = None,
) -> list[dict[str, Any]]:
    tokens = set(tokenize(goal))
    expanded = expand_tokens(list(tokens))
    expert_cats = {c.lower() for c in expert.get("categories", [])}
    expert_groups = {g.lower() for g in expert.get("groups", [])}

    scored: list[tuple[int, str, dict[str, Any]]] = []
    for skill in skills:
        slug = skill.get("slug") or skill.get("name") or ""
        if not slug:
            continue
        if locked_slugs is not None and slug not in locked_slugs:
            continue

        repo_cat = skill.get("repo", "").replace("skills-", "").lower()
        skill_cat = skill.get("category", "").lower()
        if category and category.lower() not in (repo_cat, skill_cat):
            continue

        slug_tokens = set(tokenize(slug.replace("-", " ")))
        title_tokens = set(tokenize(skill.get("title", "")))
        group_name = skill.get("group", "")
        group_tokens = set(tokenize(group_name))
        desc_tokens = set(tokenize(skill.get("description", "")))

        direct_score = (
            len(tokens & slug_tokens) * 5
            + len(tokens & title_tokens) * 4
            + len(tokens & group_tokens) * 3
            + len(tokens & desc_tokens) * 2
        )
        synonym_tokens = expanded - tokens
        syn_score = (
            len(synonym_tokens & slug_tokens) * 3
            + len(synonym_tokens & title_tokens) * 2
            + len(synonym_tokens & group_tokens) * 2
            + len(synonym_tokens & desc_tokens) * 1
        )

        total = direct_score + syn_score
        if repo_cat in expert_cats:
            total += 4 if total > 0 else 1
        if group_name.lower() in expert_groups:
            total += 3 if total > 0 else 1

        if total > 0:
            scored.append((total, slug, skill))

    scored.sort(key=lambda item: (-item[0], item[1]))
    results = [{**item[2], "score": item[0]} for item in scored[: max(1, limit)]]
    return results


def fetch_skill_body(
    skill: dict[str, Any],
    repos_map: dict[str, str],
    root_dir: Path,
    ref: str = "v4.1.0",
) -> tuple[str, str]:
    """Return (markdown_body, source_descriptor) for a skill."""
    slug = str(skill.get("slug") or "")
    repo = str(skill.get("repo") or "")
    if not SLUG_RE.match(slug):
        raise ValueError(f"Invalid skill slug: {slug!r}")
    if repo not in repos_map:
        raise ValueError(f"Unknown repository {repo!r} for skill {slug!r}")

    # 1. Check sibling checkout first for fast offline/local determinism
    sibling_file = root_dir.parent / repo / "skills" / slug / "SKILL.md"
    if sibling_file.exists():
        return sibling_file.read_text(encoding="utf-8"), f"local:{repo}@{ref}"

    # 2. Fetch over HTTPS from raw.githubusercontent.com (pinned ref, fallback main)
    for branch in (ref, "main"):
        raw_url = f"https://raw.githubusercontent.com/poorvith-mp/{repo}/{branch}/skills/{slug}/SKILL.md"
        req = urllib.request.Request(raw_url, headers={"User-Agent": "skillary-agents/5.0.0"})
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                body = resp.read().decode("utf-8")
                return body, raw_url
        except (urllib.error.URLError, TimeoutError):
            continue

    raise RuntimeError(f"Could not fetch SKILL.md for {repo}/skills/{slug}")


def pull_skills(
    matched_skills: list[dict[str, Any]],
    repos_map: dict[str, str],
    root_dir: Path,
    install_dir: Path,
    ref: str = "v4.1.0",
) -> list[dict[str, Any]]:
    pulled: list[dict[str, Any]] = []
    install_dir.mkdir(parents=True, exist_ok=True)

    for skill in matched_skills:
        slug = skill["slug"]
        body, source = fetch_skill_body(skill, repos_map, root_dir, ref=ref)
        digest = hashlib.sha256(body.encode("utf-8")).hexdigest()
        dest_file = install_dir / slug / "SKILL.md"
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        dest_file.write_text(body, encoding="utf-8")
        pulled.append(
            {
                **skill,
                "installed_path": str(dest_file),
                "source": source,
                "sha256": digest,
                "body": body,
            }
        )
    return pulled


def build_action_guide(
    goal: str,
    expert: dict[str, Any],
    skills: list[dict[str, Any]],
    model: str = "universal",
) -> str:
    lines = [
        f"# Active Expert Guide: {expert['title']}",
        "",
        f"- **Expert Persona ID**: `{expert['id']}`",
        f"- **Target Model Profile**: `{model}`",
        f"- **Categories**: {', '.join(f'`{c}`' for c in expert.get('categories', []))}",
        f"- **User Goal**: {goal}",
        "",
        "## 1. Mandatory Action Protocol",
        "",
    ]
    for idx, step in enumerate(expert.get("default_action_steps", []), start=1):
        lines.append(f"{idx}. {step}")

    lines.extend(
        [
            "",
            "## 2. Matched Skillary Skills (v4.1.0)",
            "",
            "| Skill Slug | Category | Group | Repo |",
            "|---|---|---|---|",
        ]
    )
    for s in skills:
        lines.append(
            f"| `{s['slug']}` | {s.get('category', '')} | {s.get('group', '')} | `{s.get('repo', '')}` |"
        )

    lines.extend(["", "## 3. Mounted Skill Instructions", ""])
    for s in skills:
        lines.append(f"### Skill: `{s['slug']}` ({s.get('title', s['slug'])})")
        lines.append(f"- **Source Repo**: `{s.get('repo', '')}`")
        lines.append(f"- **Summary**: {s.get('description', '')}")
        if s.get("installed_path"):
            lines.append(f"- **Installed Path**: `{s['installed_path']}`")
        if s.get("sha256"):
            lines.append(f"- **SHA-256**: `{s['sha256']}`")
        lines.append("")
        if s.get("body"):
            lines.append("```markdown")
            lines.append(s["body"].strip())
            lines.append("```")
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="skillary-agent",
        description="Route a prompt to a domain expert, pull required SKILL.md files on demand, and emit a universal model action guide.",
    )
    parser.add_argument("--goal", required=True, help="User prompt, bug description, or goal.")
    parser.add_argument(
        "--model",
        default="universal",
        help="Target model identifier (e.g. gemini-4-argon, gemini-3.8-flash, opus-5.5, fable-5.1, gpt-6-astra, or any OpenRouter/local model).",
    )
    parser.add_argument("--category", default=None, help="Optional category filter (e.g. developer, design, gamedev).")
    parser.add_argument("--limit", type=int, default=4, help="Maximum number of skills to mount (default: 4).")
    parser.add_argument("--pull", action="store_true", help="Fetch and install matched SKILL.md files on demand.")
    parser.add_argument(
        "--install-dir",
        type=Path,
        default=Path(".agents/skills"),
        help="Directory to install pulled SKILL.md folders (default: .agents/skills).",
    )
    parser.add_argument(
        "--emit",
        type=Path,
        default=None,
        help="Write a compiled model-agnostic action guide Markdown file (e.g. .skillary/active-expert-guide.md).",
    )
    parser.add_argument("--lock", type=Path, default=None, help="Explicit path to skillary.lock.")
    parser.add_argument("--ref", default="v4.1.0", help="Skillary catalog git ref to pull from (default: v4.1.0).")
    parser.add_argument("--json", action="store_true", help="Output routing and pull results as JSON.")
    parser.add_argument("--dry-run", action="store_true", help="Resolve expert and skills without writing files.")

    args = parser.parse_args(argv)
    root = Path(__file__).resolve().parent.parent

    skills_path = root / "index" / "skills.json"
    experts_path = root / "index" / "experts.json"
    repos_path = root / "index" / "repos.json"

    skills = json.loads(skills_path.read_text(encoding="utf-8"))
    experts = json.loads(experts_path.read_text(encoding="utf-8"))
    repos_map = json.loads(repos_path.read_text(encoding="utf-8"))

    lock_file = find_lockfile(args.lock)
    locked_slugs = load_locked_slugs(lock_file)
    if locked_slugs is not None and not args.json:
        print(f"using skillary.lock ({len(locked_slugs)} skills)")

    expert = select_expert(args.goal, experts)
    matched = rank_skills(
        args.goal,
        expert,
        skills,
        limit=args.limit,
        category=args.category,
        locked_slugs=locked_slugs,
    )

    if args.pull and not args.dry_run:
        matched = pull_skills(matched, repos_map, root, args.install_dir, ref=args.ref)
    elif args.emit and not args.dry_run:
        # Load skill bodies in-memory for the emitted guide even if --pull wasn't passed
        hydrated: list[dict[str, Any]] = []
        for s in matched:
            try:
                body, source = fetch_skill_body(s, repos_map, root, ref=args.ref)
                hydrated.append({**s, "source": source, "body": body})
            except Exception:
                hydrated.append(s)
        matched = hydrated

    guide_text = build_action_guide(args.goal, expert, matched, model=args.model)

    if args.emit and not args.dry_run:
        args.emit.parent.mkdir(parents=True, exist_ok=True)
        args.emit.write_text(guide_text, encoding="utf-8")

    if args.json:
        payload = {
            "goal": args.goal,
            "model": args.model,
            "expert": {
                "id": expert["id"],
                "title": expert["title"],
                "categories": expert.get("categories", []),
            },
            "locked": locked_slugs is not None,
            "skills": [
                {
                    "slug": s["slug"],
                    "title": s.get("title", ""),
                    "category": s.get("category", ""),
                    "group": s.get("group", ""),
                    "repo": s.get("repo", ""),
                    "score": s.get("score", 0),
                    "installed_path": s.get("installed_path"),
                    "sha256": s.get("sha256"),
                }
                for s in matched
            ],
            "emitted_guide": str(args.emit) if (args.emit and not args.dry_run) else None,
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    print(f"Expert: {expert['title']} ({expert['id']}) | Model: {args.model}")
    for s in matched:
        status = f" -> {s['installed_path']}" if s.get("installed_path") else ""
        print(f"  - {s['slug']} [{s.get('repo')}] ({s.get('group')}){status}")
    if args.emit and not args.dry_run:
        print(f"Emitted action guide: {args.emit}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
