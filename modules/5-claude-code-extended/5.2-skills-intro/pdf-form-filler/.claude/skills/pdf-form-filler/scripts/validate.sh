#!/usr/bin/env bash
# Validate a field-values mapping against a PDF form schema.
#
# Usage: scripts/validate.sh FORM_FIELDS_JSON FIELD_VALUES_JSON
#
# Exit codes:
#   0  all values map to known fields, types compatible
#   1  invalid CLI arguments
#   2  validation failed - structured JSON report on stdout

set -euo pipefail

usage() {
  cat <<'EOF'
validate.sh - check field_values.json against form_fields.json

USAGE:
  scripts/validate.sh FORM_FIELDS_JSON FIELD_VALUES_JSON

ARGUMENTS:
  FORM_FIELDS_JSON   Path to schema produced by analyze.py
  FIELD_VALUES_JSON  Path to your value mapping

EXAMPLES:
  scripts/validate.sh form_fields.json field_values.json
  uv run scripts/analyze.py form.pdf > form_fields.json && \
    scripts/validate.sh form_fields.json field_values.json

OUTPUT:
  Exit 0: silent success
  Exit 2: JSON report on stdout, structure:
    { "errors": [ { "field": "...", "code": "...", "message": "..." } ] }

ERROR CODES:
  unknown_field       Key in values does not exist in schema
  missing_required    Required field has no value
  type_mismatch       Value type incompatible with field type
  signature_field     Cannot programmatically fill /Sig fields
  read_only           Field is marked read-only
  option_not_in_list  /Ch value not in defined options
EOF
}

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  usage
  exit 0
fi

if [[ $# -ne 2 ]]; then
  echo "error: expected 2 arguments, got $#" >&2
  usage >&2
  exit 1
fi

SCHEMA="$1"
VALUES="$2"

for f in "$SCHEMA" "$VALUES"; do
  if [[ ! -r "$f" ]]; then
    echo "error: cannot read $f" >&2
    exit 1
  fi
done

# Defer to Python (jq alone struggles with type checks). One-shot inline.
python3 - "$SCHEMA" "$VALUES" <<'PY'
import json, sys

schema = json.load(open(sys.argv[1]))
values = json.load(open(sys.argv[2]))

errors = []
schema_by_name = {f["name"]: f for f in schema}

for name, value in values.items():
    if name not in schema_by_name:
        errors.append({"field": name, "code": "unknown_field",
                       "message": f"'{name}' not in form schema"})
        continue
    f = schema_by_name[name]
    if f.get("read_only"):
        errors.append({"field": name, "code": "read_only",
                       "message": "field is read-only"})
        continue
    if f["type"] == "Sig":
        errors.append({"field": name, "code": "signature_field",
                       "message": "signatures require a cert"})
        continue
    if f["type"] == "Btn" and not isinstance(value, (bool, type(None))):
        errors.append({"field": name, "code": "type_mismatch",
                       "message": "checkbox needs bool"})
    if f["type"] == "Ch" and f.get("options") and value not in f["options"]:
        errors.append({"field": name, "code": "option_not_in_list",
                       "message": f"value not in {f['options']}"})

for f in schema:
    if f.get("required") and (f["name"] not in values or values[f["name"]] is None):
        errors.append({"field": f["name"], "code": "missing_required",
                       "message": "required field has no value"})

if errors:
    json.dump({"errors": errors}, sys.stdout, indent=2)
    sys.stdout.write("\n")
    sys.exit(2)
PY
