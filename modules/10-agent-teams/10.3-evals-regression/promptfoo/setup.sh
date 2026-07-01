#!/usr/bin/env bash
# Чиста робоча копія фікстури для Promptfoo-прогону (ізоляція прогонів — та сама
# дисципліна, що в tests/agent/run.sh: жодного спільного стану між прогонами).
set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
rm -rf "$DIR/workdir"
cp -R "$DIR/../fixtures/route" "$DIR/workdir"
rm -f "$DIR/workdir/README.md"
echo "✅ workdir готовий: $DIR/workdir (копія fixtures/route)"
echo "Далі: npx promptfoo@latest eval --no-cache && npx promptfoo@latest view"
