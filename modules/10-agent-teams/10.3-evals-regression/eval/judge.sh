#!/usr/bin/env bash
# judge.sh - суддя руками: ще один claude -p читає review.md і ставить бал
# за рубрикою. Відповідь - JSON {score, reason}, її вже можна порівняти з порогом.
claude -p "$(cat eval/rubric.md)

Оціни текст рев'ю нижче. Відповідай ТІЛЬКИ JSON-об'єктом {\"score\": <число 0..1>, \"reason\": \"<одне речення>\"}.

$(cat review.md)"
