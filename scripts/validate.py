"""CI gate and validation script for skillary-agents.

Asserts:
1. No role or playbook names an individual skill slug.
2. Every playbook group exists in the index (or catalog).
3. Every capability declared in a role exists in capabilities.md.
4. No role declares 'dispatch'.
5. Deliverable filenames are unique within each playbook.
6. Goal patterns are distinct across all playbooks.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    roles_dir = root / "roles"
    playbooks_dir = root / "playbooks"
    capabilities_file = root / "capabilities.md"
    index_file = root / "index" / "skills.json"

    errors = []

    # 1. Parse capabilities from capabilities.md
    if not capabilities_file.exists():
        errors.append("capabilities.md missing")
        capabilities = set()
    else:
        text = capabilities_file.read_text(encoding="utf-8")
        capabilities = set(re.findall(r"`([a-z]+\.[a-z]+)`", text))

    # 2. Check roles
    for role_path in roles_dir.glob("*.md"):
        content = role_path.read_text(encoding="utf-8")
        lines = content.splitlines()

        for line in lines:
            if line.startswith("capabilities:"):
                declared_caps = [c.strip() for c in line.split(":", 1)[1].split(",")]
                for cap in declared_caps:
                    if cap == "dispatch":
                        errors.append(f"{role_path.name}: role cannot declare 'dispatch'")
                    elif cap and cap not in capabilities:
                        errors.append(f"{role_path.name}: unknown capability '{cap}'")

    # 3. Check playbooks
    all_goal_patterns = {}
    for pb_path in playbooks_dir.glob("*.md"):
        if pb_path.name.startswith("_"):
            continue
        content = pb_path.read_text(encoding="utf-8")
        deliverables = []

        in_frontmatter = False
        frontmatter_lines = []
        body_lines = []

        for line in content.splitlines():
            if line.strip() == "---":
                in_frontmatter = not in_frontmatter
                continue
            if in_frontmatter:
                frontmatter_lines.append(line)
            else:
                body_lines.append(line)

        # parse goal_patterns
        in_patterns = False
        patterns = []
        for fline in frontmatter_lines:
            if fline.strip().startswith("goal_patterns:"):
                in_patterns = True
                continue
            if in_patterns:
                if fline.strip().startswith("-"):
                    patterns.append(fline.strip().lstrip("-").strip())
                elif ":" in fline:
                    in_patterns = False

        for pat in patterns:
            pat_lower = pat.lower()
            if pat_lower in all_goal_patterns:
                errors.append(
                    f"Duplicate goal pattern '{pat}' in {pb_path.name} (already in {all_goal_patterns[pat_lower]})"
                )
            else:
                all_goal_patterns[pat_lower] = pb_path.name

        # check table deliverables
        for bline in body_lines:
            if "|" in bline:
                parts = [p.strip() for p in bline.split("|")]
                # format: | # | Stage | Groups | Deliverable | Parallel |
                if len(parts) >= 6 and parts[1].isdigit():
                    deliv = parts[4]
                    if deliv and deliv not in ("-", "scout output"):
                        if deliv in deliverables:
                            errors.append(
                                f"{pb_path.name}: duplicate deliverable '{deliv}' within playbook"
                            )
                        else:
                            deliverables.append(deliv)

    # 4. Check skills.json index against groups if index exists
    if index_file.exists():
        try:
            skills = json.loads(index_file.read_text(encoding="utf-8"))
            known_slugs = {s.get("name") or s.get("slug") for s in skills if isinstance(s, dict)}
            # Check that AGENTS.md, roles, and playbooks do not name a skill slug directly
            docs_to_check = [root / "AGENTS.md"] + list(roles_dir.glob("*.md")) + list(playbooks_dir.glob("*.md"))
            for doc_path in docs_to_check:
                if not doc_path.exists():
                    continue
                doc_text = doc_path.read_text(encoding="utf-8")
                ticked = set(re.findall(r"`([a-z0-9][a-z0-9-]+)`", doc_text))
                violations = ticked & known_slugs
                for v in sorted(violations):
                    errors.append(f"{doc_path.name}: names skill slug '{v}' directly")

            # Check that every playbook group reference resolves to active skills
            known_groups = {(s.get("repo", "").replace("skills-", ""), s.get("group", "")) for s in skills if s.get("group")}
            for pb_path in playbooks_dir.glob("*.md"):
                if pb_path.name.startswith("_"):
                    continue
                for line in pb_path.read_text(encoding="utf-8").splitlines():
                    if "|" in line:
                        parts = [x.strip() for x in line.split("|")]
                        if len(parts) >= 5 and parts[1].isdigit():
                            g_col = parts[3]
                            for g in re.split(r"[,;]\s*", g_col):
                                g = g.strip()
                                if ":" in g:
                                    cat, grp = g.split(":", 1)
                                    if (cat, grp) not in known_groups:
                                        errors.append(
                                            f"{pb_path.name}: playbook group '{g}' does not resolve to active skills in index"
                                        )
        except Exception as e:
            errors.append(f"Could not validate against index: {e}")

    if errors:
        print("=== Validation Failed ===", file=sys.stderr)
        for err in errors:
            print(f"ERROR: {err}", file=sys.stderr)
        return 1

    print("OK: skillary-agents validation passed (0 errors)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
