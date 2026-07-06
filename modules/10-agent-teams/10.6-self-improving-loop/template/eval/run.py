#!/usr/bin/env python3
"""Run the triage skill over the held-out set and score it with the binary judge.

    python eval/run.py            # honest score against the current SKILL.md
    python eval/run.py --buggy    # same, but truncates the skill to skill_md[:1500]

Held-out issues live in `held-out.jsonl` (text + canonical gold). The WORKING
gold is `gold.json`, a mutable copy that `make seed-bad` / `make fix-seed`
poison and restore, so the held-out set is the ground-truth anchor the loop must
not be able to rewrite.
"""
import argparse
import json
from pathlib import Path

import triage
from judge import judge

HERE = Path(__file__).resolve().parent
HELDOUT = HERE / "held-out.jsonl"
GOLD = HERE / "gold.json"
TRUNCATE = 1500  # the silent-truncation bug: skill_md[:1500]


def load_issues():
    issues = []
    for line in HELDOUT.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            issues.append(json.loads(line))
    return issues


def load_gold():
    if GOLD.exists():
        return json.loads(GOLD.read_text(encoding="utf-8"))
    # first run: seed the working gold from the canonical held-out labels
    gold = {i["id"]: i["gold"] for i in load_issues()}
    GOLD.write_text(json.dumps(gold, indent=2, ensure_ascii=False), encoding="utf-8")
    return gold


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--buggy", action="store_true",
                    help="truncate the skill to skill_md[:1500] before the judge sees it")
    args = ap.parse_args()

    skill_text = triage.load_skill(truncate=TRUNCATE if args.buggy else None)
    issues = load_issues()
    gold = load_gold()

    predictions = {i["id"]: triage.classify(i["title"] + " " + i["body"], skill_text)
                   for i in issues}
    score, total, misses = judge(predictions, gold)

    tag = " [--buggy: skill_md[:1500]]" if args.buggy else ""
    print(f"held-out score: {score}/{total}{tag}")
    if misses:
        print("misclassified:")
        for issue_id, pred, gold_label in misses:
            print(f"  {issue_id:<28} predicted={pred:<8} gold={gold_label}")
    else:
        print("all issues classified correctly")
    return score


if __name__ == "__main__":
    main()
