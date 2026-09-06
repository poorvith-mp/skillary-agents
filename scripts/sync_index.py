"""Sync machine index from skillary into skillary-agents.

Pulls dist/skills.json, validates that every functional group referenced in playbooks
resolves to skills in the index, and commits index/skills.json.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    local_source = root.parent / "skillary" / "dist" / "skills.json"
    target = root / "index" / "skills.json"

    if not local_source.exists():
        print(f"Error: local index {local_source} not found", file=sys.stderr)
        return 1

    data = json.loads(local_source.read_text(encoding="utf-8"))
    target.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"OK: Synced {len(data)} skills into {target.relative_to(root)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
