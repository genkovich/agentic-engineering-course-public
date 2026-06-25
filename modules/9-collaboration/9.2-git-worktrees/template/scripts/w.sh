# scripts/w.sh — raise an isolated worktree in one call (incident.io-style `w`).
#
# This file is COMMITTED in the repo, so the screencast does `source scripts/w.sh`
# instead of assuming the function already lives in your ~/.zshrc. In a real
# project you would drop this into your shell profile once.
#
# Usage:
#   source scripts/w.sh
#   w <feature>
#
# One call: create the worktree, copy the git-ignored .env into it, assign a
# free port, write that port into the worktree's .env, and print how to serve.
w() {
  feature="$1"
  if [ -z "$feature" ]; then
    echo "usage: w <feature>" >&2
    return 1
  fi

  root="$(git rev-parse --show-toplevel)" || return 1
  prefix="$(basename "$root")"
  dir="$root/../${prefix}-${feature}"

  # 1. create the worktree on a fresh branch (sibling dir, grouped by prefix)
  git worktree add "$dir" -b "$feature" >/dev/null || return 1

  # 2. copy the git-ignored .env into the fresh checkout
  if [ -f "$root/.env" ]; then
    cp "$root/.env" "$dir/.env"
  fi

  # 3. assign a free port and write it into THIS worktree's .env
  port="$(python3 -c 'import socket; s=socket.socket(); s.bind(("",0)); print(s.getsockname()[1]); s.close()')"
  if [ -f "$dir/.env" ]; then
    if grep -q '^PORT=' "$dir/.env"; then
      sed "s/^PORT=.*/PORT=${port}/" "$dir/.env" > "$dir/.env.tmp" && mv "$dir/.env.tmp" "$dir/.env"
    else
      printf 'PORT=%s\n' "$port" >> "$dir/.env"
    fi
  fi

  echo "worktree ready: ${prefix}-${feature}  (branch ${feature}, PORT=${port})"
  echo "  cd ${dir} && python3 app.py    # serves on its own port"
}
