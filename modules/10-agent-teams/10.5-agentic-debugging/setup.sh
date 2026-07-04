#!/usr/bin/env bash
# setup.sh — build sandbox/ : a self-contained git repo with 16 seed commits of a
# tiny Node billing package (invoice math). A regression is seeded at commit #9
# ("refactor: extract discount application"): the extracted applyDiscount rounds
# the discounted amount to whole cents, which quietly shifts the final total by a
# cent for one edge case (a fractional discount then a fractional tax rate). The
# bug reproduces on HEAD and every commit 9..16, and NOT on 1..8 — so
# `git bisect run ../reproduce.sh` walks straight to commit #9.
#
# Deterministic: fixed author/committer dates and identity → identical commit
# hashes on every rebuild. The culprit hash is written to sandbox/.culprit for
# verification (git-ignored, never committed, never shown in the README).
# Re-runnable: wipes sandbox/ and rebuilds.
set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SB="$ROOT/sandbox"

rm -rf "$SB"
mkdir -p "$SB"
cd "$SB"

git init -q -b main
git config user.email "demo-author@example.com"
git config user.name "Demo Author"
git config commit.gpgsign false
git config core.autocrlf false

# seed <n> <subject> [body] — stage everything and commit with a fixed date
# (2026-03-<01+n>) and a Co-Authored-By trailer, mirroring agent-made history.
seed() {
  local n="$1" subject="$2" body="${3:-}"
  local d
  d="2026-03-$(printf '%02d' $((1 + n)))T10:00:00"
  export GIT_AUTHOR_DATE="$d" GIT_COMMITTER_DATE="$d"
  git add -A
  if [ -n "$body" ]; then
    git commit -q --no-verify \
      -m "$subject" -m "$body" \
      -m "Co-Authored-By: Claude <noreply@anthropic.com>"
  else
    git commit -q --no-verify \
      -m "$subject" \
      -m "Co-Authored-By: Claude <noreply@anthropic.com>"
  fi
}

# ─────────────────────────────────────────────────────────────────────────────
# Commit 1 — scaffold with a working invoice builder (inline, CORRECT discount).
# ─────────────────────────────────────────────────────────────────────────────
mkdir -p src test

cat > package.json <<'EOF'
{
  "name": "billing",
  "private": true,
  "version": "0.1.0",
  "description": "Tiny invoice builder (subtotal, discount, tax, rounding). Pure node, no dependencies.",
  "main": "src/invoice.js",
  "scripts": {
    "test": "node --test"
  }
}
EOF

cat > .gitignore <<'EOF'
node_modules/
.culprit
.DS_Store
EOF

cat > README.md <<'EOF'
# billing

Tiny invoice builder for the debugging demo. Computes an invoice from line items:

    subtotal → discount → tax → total (rounded to whole cents)

## Usage

```js
const { buildInvoice } = require("./src/invoice");

buildInvoice([{ price: 19.99, qty: 3 }], { discountPercent: 10, taxPercent: 8.25 });
// { subtotal, discount, tax, total }
```
EOF

cat > src/invoice.js <<'EOF'
// Build an invoice from line items: subtotal -> discount -> tax -> total.
// The final total is rounded to whole cents.
function buildInvoice(lineItems, { discountPercent = 0, taxPercent = 0 } = {}) {
  const subtotal = lineItems.reduce((sum, it) => sum + it.price * it.qty, 0);
  const discounted = subtotal - (subtotal * discountPercent) / 100;
  const tax = (discounted * taxPercent) / 100;
  const total = Math.round((discounted + tax) * 100) / 100;
  return { subtotal, discount: subtotal - discounted, tax, total };
}

module.exports = { buildInvoice };
EOF
seed 1 "chore: scaffold billing package with invoice builder" \
  "Pure node (no deps). buildInvoice computes subtotal, discount, tax and a cent-rounded total."

# ─────────────────────────────────────────────────────────────────────────────
# Commit 2 — happy-path unit tests (deliberately do NOT cover the edge case
# that the seeded bug breaks, so the suite stays green throughout).
# ─────────────────────────────────────────────────────────────────────────────
cat > test/invoice.test.js <<'EOF'
const test = require("node:test");
const assert = require("node:assert");
const { buildInvoice } = require("../src/invoice");

test("subtotal sums line items", () => {
  const inv = buildInvoice([{ price: 10, qty: 2 }, { price: 5, qty: 1 }]);
  assert.strictEqual(inv.subtotal, 25);
});

test("no discount or tax means total equals subtotal", () => {
  const inv = buildInvoice([{ price: 7, qty: 3 }]);
  assert.strictEqual(inv.total, 21);
});
EOF
seed 2 "test(billing): cover subtotal and no-op invoice"

# ─────────────────────────────────────────────────────────────────────────────
# Commit 3 — docs.
# ─────────────────────────────────────────────────────────────────────────────
cat >> README.md <<'EOF'

## Options

- `discountPercent` — percentage discount applied to the subtotal.
- `taxPercent` — percentage tax applied after the discount.
EOF
seed 3 "docs(billing): document buildInvoice options"

# ─────────────────────────────────────────────────────────────────────────────
# Commit 4 — CLI entry (uses buildInvoice; math unchanged).
# ─────────────────────────────────────────────────────────────────────────────
cat > src/cli.js <<'EOF'
#!/usr/bin/env node
// Print a demo invoice as JSON.
const { buildInvoice } = require("./invoice");

const inv = buildInvoice(
  [{ price: 19.99, qty: 3 }],
  { discountPercent: 10, taxPercent: 8.25 }
);
console.log(JSON.stringify(inv, null, 2));
EOF
seed 4 "feat(billing): add CLI entry to print an invoice"

# ─────────────────────────────────────────────────────────────────────────────
# Commit 5 — one more green test (whole-dollar item; unaffected by the bug).
# ─────────────────────────────────────────────────────────────────────────────
cat >> test/invoice.test.js <<'EOF'

test("discount and tax on a whole-dollar item", () => {
  const inv = buildInvoice([{ price: 100, qty: 1 }], { discountPercent: 10, taxPercent: 20 });
  assert.strictEqual(inv.total, 108);
});
EOF
seed 5 "test(billing): add discount-and-tax happy path"

# ─────────────────────────────────────────────────────────────────────────────
# Commit 6 — refactor: extract computeSubtotal (result identical).
# ─────────────────────────────────────────────────────────────────────────────
cat > src/invoice.js <<'EOF'
// Build an invoice from line items: subtotal -> discount -> tax -> total.
// The final total is rounded to whole cents.
function computeSubtotal(lineItems) {
  return lineItems.reduce((sum, it) => sum + it.price * it.qty, 0);
}

function buildInvoice(lineItems, { discountPercent = 0, taxPercent = 0 } = {}) {
  const subtotal = computeSubtotal(lineItems);
  const discounted = subtotal - (subtotal * discountPercent) / 100;
  const tax = (discounted * taxPercent) / 100;
  const total = Math.round((discounted + tax) * 100) / 100;
  return { subtotal, discount: subtotal - discounted, tax, total };
}

module.exports = { buildInvoice, computeSubtotal };
EOF
seed 6 "refactor(billing): extract computeSubtotal helper"

# ─────────────────────────────────────────────────────────────────────────────
# Commit 7 — housekeeping (package.json engines).
# ─────────────────────────────────────────────────────────────────────────────
cat > package.json <<'EOF'
{
  "name": "billing",
  "private": true,
  "version": "0.1.0",
  "description": "Tiny invoice builder (subtotal, discount, tax, rounding). Pure node, no dependencies.",
  "main": "src/invoice.js",
  "engines": {
    "node": ">=18"
  },
  "scripts": {
    "test": "node --test"
  }
}
EOF
seed 7 "chore(billing): declare node>=18 engine"

# ─────────────────────────────────────────────────────────────────────────────
# Commit 8 — docs (rounding note). Still CORRECT; this is the last good commit.
# ─────────────────────────────────────────────────────────────────────────────
cat >> README.md <<'EOF'

## Rounding

Only the final total is rounded, to whole cents.
EOF
seed 8 "docs(billing): note the total rounding rule"

# ─────────────────────────────────────────────────────────────────────────────
# Commit 9 — THE CULPRIT. "refactor: extract discount application".
# The extracted applyDiscount rounds the discounted amount to whole cents. Looks
# tidy, but it drops the sub-cent fraction the tax step used to see, so the final
# total lands a cent low for a fractional-discount + fractional-tax invoice.
# ─────────────────────────────────────────────────────────────────────────────
cat > src/discount.js <<'EOF'
// Apply a percentage discount to an amount.
// Returns the discounted amount rounded to whole cents so downstream steps
// work with a clean currency value.
function applyDiscount(amount, percent) {
  const discounted = amount - (amount * percent) / 100;
  return Math.round(discounted * 100) / 100;
}

module.exports = { applyDiscount };
EOF

cat > src/invoice.js <<'EOF'
// Build an invoice from line items: subtotal -> discount -> tax -> total.
// The final total is rounded to whole cents.
const { applyDiscount } = require("./discount");

function computeSubtotal(lineItems) {
  return lineItems.reduce((sum, it) => sum + it.price * it.qty, 0);
}

function buildInvoice(lineItems, { discountPercent = 0, taxPercent = 0 } = {}) {
  const subtotal = computeSubtotal(lineItems);
  const discounted = applyDiscount(subtotal, discountPercent);
  const tax = (discounted * taxPercent) / 100;
  const total = Math.round((discounted + tax) * 100) / 100;
  return { subtotal, discount: subtotal - discounted, tax, total };
}

module.exports = { buildInvoice, computeSubtotal };
EOF
seed 9 "refactor: extract discount application" \
  "Move the inline discount math into src/discount.js. applyDiscount returns a clean, cent-rounded amount."

# ─────────────────────────────────────────────────────────────────────────────
# Commit 10 — feature: money formatting helper (unrelated to the bug).
# ─────────────────────────────────────────────────────────────────────────────
cat > src/money.js <<'EOF'
// Format a dollar amount as a currency string.
function formatMoney(amount, currency = "USD") {
  const sign = amount < 0 ? "-" : "";
  const cents = Math.round(Math.abs(amount) * 100);
  const dollars = Math.floor(cents / 100);
  const rem = String(cents % 100).padStart(2, "0");
  return `${sign}${currency} ${dollars}.${rem}`;
}

module.exports = { formatMoney };
EOF
seed 10 "feat(billing): add money formatting helper"

# ─────────────────────────────────────────────────────────────────────────────
# Commit 11 — docs.
# ─────────────────────────────────────────────────────────────────────────────
cat >> README.md <<'EOF'

## Formatting

`src/money.js` exposes `formatMoney(amount, currency)` for display.
EOF
seed 11 "docs: add formatting example to README"

# ─────────────────────────────────────────────────────────────────────────────
# Commit 12 — feature: validate line item shape (throws on bad input; valid
# inputs are unaffected, bug persists).
# ─────────────────────────────────────────────────────────────────────────────
cat > src/invoice.js <<'EOF'
// Build an invoice from line items: subtotal -> discount -> tax -> total.
// The final total is rounded to whole cents.
const { applyDiscount } = require("./discount");

function computeSubtotal(lineItems) {
  return lineItems.reduce((sum, it) => sum + it.price * it.qty, 0);
}

function buildInvoice(lineItems, { discountPercent = 0, taxPercent = 0 } = {}) {
  for (const it of lineItems) {
    if (typeof it.price !== "number" || typeof it.qty !== "number") {
      throw new TypeError("each line item needs numeric price and qty");
    }
  }
  const subtotal = computeSubtotal(lineItems);
  const discounted = applyDiscount(subtotal, discountPercent);
  const tax = (discounted * taxPercent) / 100;
  const total = Math.round((discounted + tax) * 100) / 100;
  return { subtotal, discount: subtotal - discounted, tax, total };
}

module.exports = { buildInvoice, computeSubtotal };
EOF
seed 12 "feat(billing): validate line item shape"

# ─────────────────────────────────────────────────────────────────────────────
# Commit 13 — refactor: extract computeTax (still fed the buggy discounted
# amount; bug persists).
# ─────────────────────────────────────────────────────────────────────────────
cat > src/invoice.js <<'EOF'
// Build an invoice from line items: subtotal -> discount -> tax -> total.
// The final total is rounded to whole cents.
const { applyDiscount } = require("./discount");

function computeSubtotal(lineItems) {
  return lineItems.reduce((sum, it) => sum + it.price * it.qty, 0);
}

function computeTax(amount, taxPercent) {
  return (amount * taxPercent) / 100;
}

function buildInvoice(lineItems, { discountPercent = 0, taxPercent = 0 } = {}) {
  for (const it of lineItems) {
    if (typeof it.price !== "number" || typeof it.qty !== "number") {
      throw new TypeError("each line item needs numeric price and qty");
    }
  }
  const subtotal = computeSubtotal(lineItems);
  const discounted = applyDiscount(subtotal, discountPercent);
  const tax = computeTax(discounted, taxPercent);
  const total = Math.round((discounted + tax) * 100) / 100;
  return { subtotal, discount: subtotal - discounted, tax, total };
}

module.exports = { buildInvoice, computeSubtotal, computeTax };
EOF
seed 13 "refactor(billing): extract computeTax helper"

# ─────────────────────────────────────────────────────────────────────────────
# Commit 14 — changelog.
# ─────────────────────────────────────────────────────────────────────────────
cat > CHANGELOG.md <<'EOF'
# Changelog

## Unreleased
- Line item validation.
- Money formatting helper.
- Invoice builder with subtotal, discount, tax and rounding.
EOF
seed 14 "chore: add CHANGELOG"

# ─────────────────────────────────────────────────────────────────────────────
# Commit 15 — CLI smoke test.
# ─────────────────────────────────────────────────────────────────────────────
cat > test/cli.test.js <<'EOF'
const test = require("node:test");
const assert = require("node:assert");
const { execFileSync } = require("node:child_process");
const path = require("node:path");

test("cli prints an invoice as json", () => {
  const out = execFileSync("node", [path.join(__dirname, "..", "src", "cli.js")], { encoding: "utf8" });
  const inv = JSON.parse(out);
  assert.strictEqual(typeof inv.total, "number");
});
EOF
seed 15 "test(billing): add CLI smoke test"

# ─────────────────────────────────────────────────────────────────────────────
# Commit 16 — docs (HEAD; bug still present).
# ─────────────────────────────────────────────────────────────────────────────
cat >> README.md <<'EOF'

## Notes

Discounts are stored as clean currency amounts before tax is applied.
EOF
seed 16 "docs(billing): note discount rounding policy"

# ─────────────────────────────────────────────────────────────────────────────
# Record the culprit (commit #9) hash for verification. Git-ignored.
# ─────────────────────────────────────────────────────────────────────────────
CULPRIT="$(git rev-list --reverse HEAD | sed -n '9p')"
printf '%s\n' "$CULPRIT" > "$SB/.culprit"

echo ""
echo "sandbox ready at $SB"
echo "  commits:  $(git rev-list --count HEAD) (bug seeded at #9, hidden in .culprit)"
echo "  HEAD:     $(git rev-parse --short HEAD)"
echo "  run:      make repro     # reproduce.sh fails on HEAD (exit 1)"
echo "            make bisect    # git bisect run finds commit #9"
