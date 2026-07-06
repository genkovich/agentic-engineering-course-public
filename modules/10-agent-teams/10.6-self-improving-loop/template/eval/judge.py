#!/usr/bin/env python3
"""The binary, deterministic judge: predicted label == gold label.

This is the spine of the loop. It never reasons, never rationalises, and cannot
be talked into a higher score. Contrast it with `rubric.md`, the subjective
critic a same-model judge would rubber-stamp. Returns (score, total, misses).
"""


def judge(predictions, gold):
    misses = []
    correct = 0
    for issue_id, gold_label in gold.items():
        pred = predictions.get(issue_id)
        if pred == gold_label:
            correct += 1
        else:
            misses.append((issue_id, pred, gold_label))
    return correct, len(gold), misses
