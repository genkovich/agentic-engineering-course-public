# Audit report: {url}

**Status:** {http_status}
**Date:** {date}
**Verdict:** {pass_or_fail}

## Summary

{one or two sentences: how many findings, what severity dominates, is the endpoint shippable as-is}

## Findings

### {category} - {severity}

**What:** {message}
**Suggested fix:** {one-line proposal, or "out of scope of runtime audit"}

(repeat per finding; if there are none, write "No findings - the runtime probe did not flag this endpoint")

## Verification steps already performed

- [x] Endpoint reachability check
- [x] Status code classification
- [x] Content-Type header presence
- [x] Body shape (JSON validity if claimed)
- [x] Cache-Control / ETag / Last-Modified presence
- [x] Health-vs-ready discrimination (only for `/health`, `/ready`)

## Out of scope

- Latency under load (single-shot wall-clock only)
- Authn / authz semantics beyond `401` / `403` reporting
- Downstream dependency health (DB, cache, queues)
- Static source review (this is a black-box probe)

## Next step proposed

{exactly one action the user can take next, e.g. "set explicit Content-Type: application/json on this handler" or "split /health into /live and /ready"}
