# Error catalog

> When to read this: when `analyze.py` or `validate.sh` exits non-zero with an error code you do not recognize, or when filling a form fails silently (output PDF has empty fields).

## Exit codes from bundled scripts

| Script | Exit | Meaning | Fix |
|---|---|---|---|
| `analyze.py` | 0 | Success, JSON on stdout | - |
| `analyze.py` | 1 | Invalid CLI args | Run `--help` for usage |
| `analyze.py` | 2 | PDF has no AcroForm | Re-export the PDF as a form, or fall back to overlay-text mode |
| `analyze.py` | 3 | PDF is encrypted, no password | Pass `--password=...` |
| `analyze.py` | 4 | XFA form detected | Out of scope. Tell the user we do not handle XFA. |
| `validate.sh` | 0 | All values map to known fields, types compatible | - |
| `validate.sh` | 1 | Invalid CLI args | Run `--help` for usage |
| `validate.sh` | 2 | Validation failed - see JSON report on stdout | Read each `error.code`, fix `field_values.json`, rerun |

## Validation error codes (from `validate.sh`)

| `error.code` | Meaning | Fix |
|---|---|---|
| `unknown_field` | A key in `field_values.json` does not exist in the form | Remove the key, or check spelling against `form_fields.json` |
| `missing_required` | A field marked Required has no value | Add the key with a non-null value |
| `type_mismatch` | Value type incompatible with field type | Booleans for checkboxes, strings for `/Tx`, valid option for `/Ch` |
| `signature_field` | Attempt to set a value on a `/Sig` field | Remove that key. Signatures need a real cert. |
| `read_only` | Attempt to set a value on a read-only field | Remove the key. Read-only fields cannot be filled. |
| `option_not_in_list` | `/Ch` value is not one of the field's defined options | Open `form_fields.json`, check the `options` array, pick a valid one |

## Silent-failure symptoms

**Output PDF opens, but fields are empty.** Likely cause: appearance streams not regenerated. Add `field.AP = None` after every `.V` assignment.

**Output PDF opens in Adobe Reader correctly but blank in Preview.app.** Same cause - Preview is more strict about regeneration. The fix is the same.

**Checkbox shows "x" but field reads as off.** Wrong export value. Use `pikepdf.Name("/Yes")` not `pikepdf.String("Yes")`.

**Filled value gets truncated.** PDF text fields have a max-length attribute (`/MaxLen`). The validator should catch this - if it did not, the form has no `/MaxLen` declared and the viewer is enforcing its own limit.

## Library-specific exceptions

### `pikepdf.PasswordError`

```
pikepdf._core.PasswordError: input.pdf: invalid password
```

Two cases: no password supplied for encrypted PDF, or wrong password. Pass `password="..."` to `pikepdf.open()`.

### `pikepdf.PdfError: object stream missing`

```
pikepdf._core.PdfError: object stream object 42 0 missing
```

Damaged xref table. Try recovery mode:

```python
pikepdf.open(path, attempt_recovery=True)
```

If that fails, the PDF is too damaged to fix programmatically.

### `KeyError: '/AcroForm'`

Direct access without checking:

```python
# Wrong - raises KeyError on non-form PDFs
fields = pdf.acroform.fields
```

Always check first:

```python
if "/AcroForm" in pdf.Root:
    fields = pdf.acroform.fields
```

`analyze.py` does this check and exits 2 with a friendly message instead of letting the exception propagate.
