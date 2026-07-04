#!/usr/bin/env bash
# reproduce.sh — minimal, dependency-free repro of the invoice bug.
#
# It exercises buildInvoice on a fractional-discount + fractional-tax invoice and
# checks the final total. This is the STABLE public interface that has existed
# since the first commit, so the script runs unchanged against ANY commit that
# `git bisect` checks out. That is what makes it a bisect-runnable test:
#
#   exit 0 -> total correct  (git bisect: "good")
#   exit 1 -> total wrong    (git bisect: "bad")
#
# Run it from inside the repo under test (its CWD is the checked-out sandbox):
#   cd sandbox && bash ../reproduce.sh
#   git bisect run bash ../reproduce.sh
set -u

node -e '
const path = require("path");
const { buildInvoice } = require(path.join(process.cwd(), "src", "invoice.js"));

// 19.99 x 3 = 59.97 subtotal; 10% discount then an 8.25% tax rate.
const inv = buildInvoice(
  [{ price: 19.99, qty: 3 }],
  { discountPercent: 10, taxPercent: 8.25 }
);

const expected = 58.43;
if (inv.total !== expected) {
  console.error(`FAIL: total=${inv.total} expected=${expected}`);
  process.exit(1);
}
console.log(`OK: total=${inv.total}`);
'
