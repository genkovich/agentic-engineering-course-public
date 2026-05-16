# PDF form fill report

## Summary

- Input: `<input.pdf>`
- Output: `<output.pdf>`
- Fields total: `<N>`
- Fields filled: `<M>`
- Fields skipped (read-only / signature): `<K>`

## Filled fields

| Name | Type | Value |
|---|---|---|
| `<field_name>` | `Tx` | `<value>` |

## Skipped fields

| Name | Reason |
|---|---|
| `<field_name>` | `read_only` / `signature_field` / `not in mapping` |

## Verification

- Re-analysis of `<output.pdf>`: `<all values present>` / `<discrepancy in N fields>`
- Notes: `<any anomalies, e.g., appearance-stream regen needed>`
