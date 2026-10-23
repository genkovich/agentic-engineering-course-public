#!/usr/bin/env -S uv run --quiet
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pdfplumber>=0.11",
#   "pikepdf>=8.0",
# ]
# ///
"""Analyze a PDF for AcroForm fields and emit JSON on stdout.

Usage: uv run scripts/analyze.py [--password=PWD] PDF_PATH

Exit codes:
  0  success, JSON on stdout
  1  invalid CLI arguments
  2  PDF has no AcroForm dictionary
  3  PDF is encrypted and no/invalid password supplied
  4  XFA form detected (out of scope for this skill)
"""

import argparse
import json
import sys

import pdfplumber
import pikepdf
from pdfminer.pdftypes import resolve1


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect AcroForm fields in a PDF")
    parser.add_argument("pdf", help="path to PDF file")
    parser.add_argument("--password", default="", help="password if PDF is encrypted")
    args = parser.parse_args()

    try:
        with pdfplumber.open(args.pdf, password=args.password) as pdf:
            # pdfminer keys the catalog without the leading slash: "AcroForm", not "/AcroForm"
            acroform = resolve1(pdf.doc.catalog.get("AcroForm"))
            if not acroform:
                print(f"error: {args.pdf} has no AcroForm dictionary", file=sys.stderr)
                return 2
            if acroform.get("XFA"):
                print(f"error: {args.pdf} is an XFA form (out of scope)", file=sys.stderr)
                return 4
    except Exception as exc:
        if "password" in str(exc).lower():
            print(f"error: {args.pdf} is encrypted - pass --password", file=sys.stderr)
            return 3
        raise

    fields = []
    with pikepdf.open(args.pdf, password=args.password) as pdf:
        # walk the raw /Fields tree: pikepdf's AcroFormField wrappers have no .get()
        def walk(node, parent_name="", inherited_ft=None, inherited_ff=0):
            name = str(node.get("/T", ""))
            full = f"{parent_name}.{name}" if parent_name and name else (name or parent_name)
            ft = node.get("/FT", inherited_ft)
            ff = int(node.get("/Ff", inherited_ff) or 0)
            kids = [k for k in node.get("/Kids", []) if "/T" in k]
            if kids:
                for kid in kids:
                    walk(kid, full, ft, ff)
                return
            opts = []
            for opt in node.get("/Opt", []) or []:
                # /Opt items are either strings or [export_value, display_text] pairs
                opts.append(str(opt[0]) if isinstance(opt, pikepdf.Array) else str(opt))
            fields.append({
                "name": full,
                "type": str(ft or "/Tx").lstrip("/"),
                "required": bool(ff & 0b10),
                "read_only": bool(ff & 0b01),
                "options": opts or None,
            })

        for field in pdf.Root.AcroForm.get("/Fields", []):
            walk(field)

    json.dump(fields, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
