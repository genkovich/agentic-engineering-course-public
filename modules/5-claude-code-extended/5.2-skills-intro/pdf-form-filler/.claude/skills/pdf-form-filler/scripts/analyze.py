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


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect AcroForm fields in a PDF")
    parser.add_argument("pdf", help="path to PDF file")
    parser.add_argument("--password", default="", help="password if PDF is encrypted")
    args = parser.parse_args()

    try:
        with pdfplumber.open(args.pdf, password=args.password) as pdf:
            if "/AcroForm" not in pdf.doc.catalog:
                print(f"error: {args.pdf} has no AcroForm dictionary", file=sys.stderr)
                return 2
            if pdf.doc.catalog.get("/AcroForm", {}).get("/XFA"):
                print(f"error: {args.pdf} is an XFA form (out of scope)", file=sys.stderr)
                return 4
    except Exception as exc:
        if "password" in str(exc).lower():
            print(f"error: {args.pdf} is encrypted - pass --password", file=sys.stderr)
            return 3
        raise

    fields = []
    with pikepdf.open(args.pdf, password=args.password) as pdf:
        for field in getattr(pdf.acroform, "fields", []) or []:
            ft = str(field.get("/FT", ""))
            ff = int(field.get("/Ff", 0) or 0)
            fields.append({
                "name": str(field.get("/T", "")),
                "type": ft.lstrip("/") or "Tx",
                "required": bool(ff & 0b10),
                "read_only": bool(ff & 0b01),
                "options": [str(o) for o in field.get("/Opt", []) or []] or None,
            })

    json.dump(fields, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
