"""Check that relative links in the repository's Markdown files point at files that exist.

    python tools/check_links.py                 check every tracked .md file
    python tools/check_links.py README.md docs  check these files or folders only

Standard library only; reads files, changes nothing, uses no network. Web links (http, https,
mailto) and in-page anchors are not checked. Exit status 1 if any relative link is broken.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"(?<!\!)\[[^\]\n]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
FENCE = re.compile(r"^(```|~~~)")


def tracked_markdown() -> list[Path]:
    out = subprocess.run(["git", "ls-files", "*.md"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    return [ROOT / line for line in out.splitlines() if line.strip()]


def links(path: Path):
    in_fence = False
    for number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        if FENCE.match(line.strip()):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for target in LINK.findall(re.sub(r"`[^`]*`", "", line)):
            yield number, target


def main() -> int:
    chosen = [ROOT / arg for arg in sys.argv[1:]]
    files = tracked_markdown()
    if chosen:
        files = [f for f in files if any(f == c or c in f.parents for c in chosen)]
    broken, checked = [], 0
    for path in files:
        for number, target in links(path):
            if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target) or target.startswith("#"):
                continue
            checked += 1
            local = unquote(target.split("#", 1)[0].split("?", 1)[0])
            resolved = (ROOT / local.lstrip("/")) if local.startswith("/") else (path.parent / local)
            if not resolved.exists():
                broken.append(f"{path.relative_to(ROOT).as_posix()}:{number}: {target}")
    print(f"{checked} relative links in {len(files)} files; {len(broken)} broken")
    for line in broken:
        print("  " + line)
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
