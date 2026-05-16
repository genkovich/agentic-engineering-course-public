---
name: pdf-form-filler
description: >
  Fill PDF forms programmatically when the user has a fillable PDF and a set
  of values to populate. Use when the user provides a PDF with form fields
  and asks to fill them, when the user mentions "AcroForm" or "fillable PDF"
  workflows, or when batch-filling multiple forms with the same template.
  Use even if the user does not mention pdfplumber or pikepdf by name.
allowed-tools: Bash, Read, Write
disable-model-invocation: true
user-invocable: true
---

# PDF form filler

Fills fillable PDF forms (AcroForm) using a plan-validate-execute pattern. Built around two libraries: `pdfplumber` for inspection and `pikepdf` for write-back.

## Workflow

Progress checklist:
- [ ] Step 1: Analyze the form (run `scripts/analyze.py`)
- [ ] Step 2: Create field mapping (write `field_values.json`)
- [ ] Step 3: Validate mapping (run `scripts/validate.sh`)
- [ ] Step 4: Fill the form (call pikepdf, see snippet below)
- [ ] Step 5: Verify output (re-analyze the filled PDF)

### Step 1: Analyze the form

Run the bundled analyzer to discover form fields:

```bash
uv run scripts/analyze.py path/to/input.pdf > form_fields.json
```

Output is JSON: `[{"name": "...", "type": "Tx|Btn|Ch|Sig", "page": 1, "required": false}]`. If the PDF is not a fillable form (no AcroForm dictionary), the script exits with code 2 and prints a helpful message to stderr. In that case suggest the user re-export the PDF as a form, or fall back to overlay-text mode (out of scope here).

### Step 2: Create field mapping

Write `field_values.json` mapping every required field name to its value. Use `null` for fields you intend to leave blank. Example:

```json
{
  "customer_name": "Anna Kovalenko",
  "order_total": "199.00",
  "signature_date": "2026-05-05",
  "newsletter_opt_in": false
}
```

Field names must match the schema produced in step 1 character-for-character. Mismatch is the most common failure mode - the validator in step 3 catches this.

### Step 3: Validate mapping

```bash
bash scripts/validate.sh form_fields.json field_values.json
```

The validator returns exit code 0 on success, 2 on validation failure with a structured JSON error report on stdout. Fix issues and re-run until exit 0.

### Step 4: Fill the form

```python
import pikepdf, json

values = json.load(open("field_values.json"))
with pikepdf.open("input.pdf", allow_overwriting_input=False) as pdf:
    for field in pdf.acroform.fields:
        name = str(field.T)
        if name in values and values[name] is not None:
            field.V = pikepdf.String(str(values[name]))
            field.AP = None
    pdf.save("output.pdf")
```

Setting `field.AP = None` forces the PDF viewer to regenerate appearance streams - without this, fields render blank in some viewers even though the value is set internally.

### Step 5: Verify output

Re-run the analyzer on `output.pdf`. The `value` key in each entry should match `field_values.json`. If any field shows `null`, check the appearance-stream regeneration step.

## Gotchas

- **AcroForm vs XFA.** This skill handles AcroForm only. XFA forms (legacy Adobe LiveCycle) need a different toolchain - if the analyzer reports `"format": "xfa"`, stop and tell the user.
- **Checkbox values are case-sensitive.** A checkbox field expects `/Yes` or `/Off` exactly. Boolean `true` in JSON gets translated by `analyze.py` automatically; never write the string `"true"` directly.
- **Signature fields cannot be filled this way.** Type `Sig` requires a real cryptographic signature. The validator flags any attempt to set a value on a Sig field.
- **Read-only fields silently fail.** If `field.Ff & 1` is set, the field is read-only. The analyzer surfaces this as `"read_only": true`.

## When to read references

- Read `references/api-reference.md` if you need pdfplumber/pikepdf method signatures or the AcroForm field-type table.
- Read `references/error-catalog.md` if `analyze.py` or `validate.sh` exit non-zero with an error code you do not recognize.

## Output format

Write a final report following `assets/report-template.md`. Keep it short - 4 sections, no prose padding.
