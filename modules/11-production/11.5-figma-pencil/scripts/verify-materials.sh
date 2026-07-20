#!/usr/bin/env bash
set -euo pipefail

module_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
failures=0

pass() { echo "PASS  $1"; }
fail() { echo "FAIL  $1"; failures=$((failures + 1)); }

required=(
  README.md
  Makefile
  student-workbook.md
  examples/screen-brief.md
  examples/definition-of-done.md
  prompts/01-official-figma.md
  prompts/02-figma-console.md
  prompts/03-pencil.md
  prompts/04-implement-and-verify.md
)

for file in "${required[@]}"; do
  if [[ -s "$module_dir/$file" ]]; then pass "$file exists"; else fail "$file exists"; fi
done

for placeholder in '<APP_URL>' '<FIGMA_FILE_URL>' '<DESKTOP_FRAME_URL>' '<MOBILE_FRAME_URL>'; do
  if rg -q -F "$placeholder" "$module_dir/prompts" "$module_dir/examples"; then
    pass "$placeholder placeholder documented"
  else
    fail "$placeholder placeholder documented"
  fi
done

if rg -qi 'course-project|meme editor|/api/memes|sqlite' \
  "$module_dir/README.md" \
  "$module_dir/student-workbook.md" \
  "$module_dir/examples" \
  "$module_dir/prompts"; then
  fail "private demo details are absent"
else
  pass "private demo details are absent"
fi

if bash -n "$module_dir/scripts/verify-materials.sh"; then
  pass "verification script parses"
else
  fail "verification script parses"
fi

if (( failures > 0 )); then
  echo
  echo "$failures verification checks failed."
  exit 1
fi

echo
echo "PASS: module 11-5 generic materials are ready."
