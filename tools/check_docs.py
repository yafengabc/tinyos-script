"""Check that file references in this repo's docs still resolve (issue #9).

Only paths that clearly belong to this checkout are checked; references to
the sibling TinyOS tree (e.g. `docs/TESTING.md`) are left alone.  Also rejects
a few known-stale phrases that have repeatedly drifted from the code.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCAL = ("src/", "include/", "tools/", "tests/", "docs/", "spec/", "port/")
# Backticked relative paths ending in a file-ish extension.
REF = re.compile(r"`((?:src|include|tools|tests|docs|spec|port)/[^`\s]+?\.(?:c|h|inc|md|py|conf|txt|json|S))`")
STALE = (
    ("goc32/cmd/rcc", "use src/rcc/rcc.c"),
    ("spill not implemented", "spill slots exist"),
    ("still stop with a diagnostic", "the backends now cover these"),
)


def main():
    failed = 0
    docs = [ROOT / "README.md"]
    docs += sorted((ROOT / "docs").glob("*.md"))
    docs += sorted((ROOT / "spec").glob("*.md"))
    docs += sorted((ROOT / "port").rglob("*.md"))
    for path in docs:
        text = path.read_text(encoding="utf-8", errors="replace")
        for m in REF.finditer(text):
            rel = m.group(1)
            if not any(rel.startswith(p) for p in LOCAL):
                continue
            # `docs/TESTING.md` etc. live in the sibling TinyOS checkout.
            if rel in ("docs/TESTING.md", "docs/OPEN-ITEMS.md"):
                continue
            if not (ROOT / rel).exists():
                print(f"FAIL {path.relative_to(ROOT)}: missing {rel}")
                failed += 1
        for phrase, why in STALE:
            if phrase in text:
                print(f"FAIL {path.relative_to(ROOT)}: stale phrase {phrase!r} ({why})")
                failed += 1
    if failed:
        print(f"{failed} DOC CHECK(S) FAILED")
        return 1
    print(f"DOC CHECK OK ({len(docs)} files)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
