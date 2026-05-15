# API reference - pdfplumber and pikepdf for AcroForm

> When to read this: load this file when you need exact method signatures, return shapes, or AcroForm field-type semantics. Do not preload - the agent should read SKILL.md first and only reach here on demand.

## pdfplumber - inspection layer

`pdfplumber` opens PDFs and exposes content as Python objects. Use it for read-only analysis of form structure.

### `pdfplumber.open(path)` -> `PDF`

Opens a PDF for reading. Use as a context manager:

```python
with pdfplumber.open("form.pdf") as pdf:
    for page in pdf.pages:
        ...
```

### `PDF.metadata` -> `dict`

PDF metadata dictionary. For form-bearing PDFs, look for `/AcroForm` key in the trailer (not in `metadata` directly - it lives one level up).

### `PDF.pages` -> `list[Page]`

List of `Page` objects. Each page has `.width`, `.height`, `.extract_text()`, `.extract_tables()`. Form fields live on pages but the AcroForm dictionary is global.

### Detecting AcroForm presence

`pdfplumber` itself does not surface form fields directly. Use the underlying object:

```python
with pdfplumber.open(path) as pdf:
    has_form = "/AcroForm" in pdf.doc.catalog
```

If `has_form` is False, the PDF is not fillable. Suggest re-export or overlay mode.

## pikepdf - write layer

`pikepdf` is a wrapper around qpdf. Use it for any write-back operation: filling fields, regenerating appearance streams, saving the result.

### `pikepdf.open(path, **kwargs)` -> `Pdf`

Open a PDF for editing. Important kwargs:

- `allow_overwriting_input=False` (default): prevents corrupting the input file if you save to the same path
- `password="..."`: pass for encrypted PDFs

### `Pdf.acroform` -> `AcroForm`

The AcroForm dictionary. Access fields via `.fields` which returns a flat list of all form fields across all pages.

### `AcroForm.fields` -> `list[Field]`

Each `Field` has these properties relevant for filling:

| Attribute | Type | Meaning |
|---|---|---|
| `.T` | `pikepdf.String` | Field name (the key you match against `field_values.json`) |
| `.FT` | `pikepdf.Name` | Field type: `/Tx`, `/Btn`, `/Ch`, `/Sig` |
| `.V` | varies | Current value. Assign `pikepdf.String(...)` for text fields |
| `.Ff` | `int` | Flags bitmask. Bit 1 = ReadOnly, bit 2 = Required |
| `.AP` | dict or None | Appearance streams. Set to `None` after `.V` to force regeneration |
| `.Kids` | `list[Field]` | Child fields if this is a parent (radio groups, multi-page) |

### Field type table

| Type code | Meaning | How to set value |
|---|---|---|
| `/Tx` | Text field | `field.V = pikepdf.String("text content")` |
| `/Btn` (checkbox) | Checkbox | `field.V = pikepdf.Name("/Yes")` or `pikepdf.Name("/Off")` |
| `/Btn` (radio) | Radio button | `field.V = pikepdf.Name("/" + chosen_export_value)` |
| `/Ch` | Choice (dropdown / listbox) | `field.V = pikepdf.String("option label")` |
| `/Sig` | Signature | Cannot be filled programmatically without a signing cert. Skip. |

Distinguishing checkbox `/Btn` from radio `/Btn`: check `Ff` bit 16 (Pushbutton) and bit 17 (Radio). If neither is set, it is a checkbox.

### `Pdf.save(path)`

Writes the modified PDF. Pass `linearize=True` for web-optimized output (faster first-page render in browsers).

### Appearance streams - the silent failure

PDF viewers cache rendered field appearance in `field.AP`. If you change `.V` but leave `.AP` populated, many viewers (Preview.app, Chrome PDF viewer) display the cached appearance with the old or empty value.

The fix is to set `field.AP = None` after every `.V` assignment. The next time the PDF opens, the viewer regenerates the appearance from scratch and shows the new value.

If you cannot afford a regeneration round-trip (some viewers show blank fields until they open the file), pre-render appearance streams using `pikepdf.Pdf.generate_appearance_streams()`. This is slower but produces a fully self-contained PDF.

## Combining the two libraries

Use pdfplumber for inspection (`analyze.py` does this) because its API is friendlier for read-only walks. Use pikepdf for the actual write because it preserves the underlying object structure better than alternatives like `pypdf`.

A common pattern:

```python
import pdfplumber, pikepdf

# Discover
with pdfplumber.open("input.pdf") as pdf:
    has_form = "/AcroForm" in pdf.doc.catalog
    page_count = len(pdf.pages)

# Fill
if has_form:
    with pikepdf.open("input.pdf") as pdf:
        for field in pdf.acroform.fields:
            ...
        pdf.save("output.pdf")
```

The two libraries have non-overlapping concerns: pdfplumber for "what is this PDF?", pikepdf for "modify this PDF". Mixing layers (using pikepdf for inspection or pdfplumber for write) works but produces less idiomatic code.

## Encrypted forms

If the PDF is password-protected:

```python
with pikepdf.open("encrypted.pdf", password="secret") as pdf:
    ...
```

Owner password vs user password matters: opening with user password may forbid editing. If `pdf.is_encrypted` is True after `open()`, you may have opened with insufficient permissions - re-prompt for the owner password.

After filling, decide whether to preserve encryption:

```python
pdf.save("output.pdf")  # decrypted output
pdf.save("output.pdf", encryption=pikepdf.Encryption(user="u", owner="o"))  # re-encrypted
```

Default is decrypted - the user must opt in to encryption explicitly.

## Performance notes

For batch jobs (filling 100+ forms with the same template), open the template once and `pdf.copy()` per output:

```python
with pikepdf.open("template.pdf") as template:
    for record in records:
        copy = pikepdf.Pdf.new()
        copy.pages.extend(template.pages)
        # ... fill from record ...
        copy.save(f"output_{record.id}.pdf")
```

This avoids re-parsing the template on every iteration. The bottleneck for 1000+ forms is usually appearance-stream regeneration - profile before optimizing.

## Common error codes from these libraries

| Library | Exception | Likely cause |
|---|---|---|
| `pdfplumber` | `pdfplumber.utils.PDFSyntaxError` | Corrupted PDF or encryption mismatch |
| `pikepdf` | `pikepdf.PasswordError` | Wrong password or no password supplied |
| `pikepdf` | `pikepdf.PdfError: object stream` | Damaged xref table - try `pikepdf.open(path, attempt_recovery=True)` |
| `pikepdf` | `KeyError: '/AcroForm'` | PDF has no AcroForm - check before accessing `.acroform` |

For full error catalog with fixes see `error-catalog.md` in the same directory.

## Version pins (mock for course illustration)

```toml
pdfplumber = ">=0.11"
pikepdf = ">=8.0"
```

Pin lower bounds in `# /// script` blocks (PEP 723) so `uv run` resolves consistently. For long-lived projects pin upper bounds too - pikepdf has had breaking changes between major versions.
