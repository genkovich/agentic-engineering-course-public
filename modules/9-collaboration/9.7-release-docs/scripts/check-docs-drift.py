#!/usr/bin/env python3
"""check-docs-drift.py — find where docs/api.md fell behind the code. NO LLM.

This is the deterministic half of the docs-drift tool. It reads the public
`NoteBook` methods straight from the source with `ast` (no imports, no runtime),
reads the method names documented in docs/api.md, and prints the gap both ways:

  * methods in the code but missing from the doc  (the doc fell behind)
  * methods in the doc but gone from the code      (the doc describes a ghost)

The `check-docs-drift` skill calls this for the facts, then proposes the doc
edit in human language. The gap itself is found here, by parsing — not guessed
by a model. Exit code 1 when there is drift, 0 when the doc is in sync, so a CI
step (.github/workflows/docs-drift.yml) can branch on it.

Usage:  ./scripts/check-docs-drift.py [--src src/notes.py] [--doc docs/api.md]
"""

import argparse
import ast
import re
import sys
from pathlib import Path


def code_methods(src_path):
    """Public method names of the NoteBook class, read from source via ast."""
    tree = ast.parse(Path(src_path).read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "NoteBook":
            return {
                item.name
                for item in node.body
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
                and not item.name.startswith("_")
            }
    return set()


def doc_methods(doc_path):
    """Method names documented in docs/api.md (the `name(...)` cells)."""
    text = Path(doc_path).read_text(encoding="utf-8")
    # Match `add(...)`, `filter_by_tag(...)` etc. wherever they appear in prose
    # or table cells — backticked `name(` is the documented shape.
    return set(re.findall(r"`([a-z_][a-z0-9_]*)\s*\(", text))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--src", default="src/notes.py")
    parser.add_argument("--doc", default="docs/api.md")
    args = parser.parse_args(argv)

    in_code = code_methods(args.src)
    in_doc = doc_methods(args.doc)

    undocumented = sorted(in_code - in_doc)   # code grew, doc didn't
    ghost = sorted(in_doc - in_code)          # doc kept a method the code dropped

    print(f"NoteBook public methods in {args.src}: {sorted(in_code)}")
    print(f"NoteBook methods documented in {args.doc}: {sorted(in_doc)}")
    print()

    if not undocumented and not ghost:
        print("✓ no drift — docs/api.md matches the code")
        return 0

    if undocumented:
        print("✗ in the code but missing from the doc (doc fell behind):")
        for name in undocumented:
            print(f"    - NoteBook.{name}")
    if ghost:
        print("✗ in the doc but gone from the code (doc describes a ghost):")
        for name in ghost:
            print(f"    - NoteBook.{name}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
