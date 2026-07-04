#!/usr/bin/env bash
# sandbox.sh - пісочниця руками. Готового тула нема - і не треба:
# копія проєкту + свіжий git, щоразу з нуля (жодного спільного стану між прогонами).
set -e
rm -rf tmp/sandbox && mkdir -p tmp/sandbox
cp -R src .claude eval tmp/sandbox/          # усе, що потрібно агенту для задачі
cd tmp/sandbox
git init -q                                   # свій git: агент бачить чисте репо,
git add -A                                    # а грейдер зможе спитати git diff
git -c user.email=evals@example.com -c user.name=evals -c commit.gpgsign=false \
  commit -qm "seed: чистий старт пісочниці" --no-verify
echo "✅ пісочниця готова: tmp/sandbox"
