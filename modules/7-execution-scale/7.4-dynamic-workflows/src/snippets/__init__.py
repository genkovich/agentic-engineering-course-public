"""snippets - мінімальний substrate для демо dynamic workflows (Lecture 7.4).

Працюючі частини: models.Snippet, store.SnippetStore, tags.normalize_tag.
Три НЕЗАЛЕЖНІ задачі, які workflow доводить до завершення паралельно:
    - search.py  (search_by_tag / search_by_text)
    - dedupe.py  (find_duplicates)
    - export.py  (to_markdown)
Зараз усі три - заглушки з NotImplementedError. Кожна живе у власному файлі і
не пише в чужий - саме тому їх безпечно паралелити (незалежність як передумова).
"""
