#!/usr/bin/env bash
# setup.sh - чисті робочі копії для кейсів на провайдері claude-agent-sdk
# (він отримує готовий working_dir, пісочницю сам не збирає).
set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FIXTURES="$DIR/../../fixtures"
for pair in route:workdir-route nplusone:workdir-nplusone; do
  fixture="${pair%%:*}"; workdir="${pair##*:}"
  rm -rf "$DIR/$workdir"
  cp -R "$FIXTURES/$fixture" "$DIR/$workdir"
  rm -f "$DIR/$workdir/README.md"
done
echo "✅ workdir-route і workdir-nplusone готові"
