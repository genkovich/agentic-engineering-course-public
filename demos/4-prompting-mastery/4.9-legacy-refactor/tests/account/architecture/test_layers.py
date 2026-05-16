"""
Architecture tests — інваріанти нової архітектури `internal/account/`.

ДО Step 4 cutover: `internal.account` ще не існує → тести `skip`-аються.
ПІСЛЯ Step 4: тести стають жорстким барʼєром (CI failure при порушенні).
"""
from __future__ import annotations

import importlib
import inspect
import pkgutil
import re

import pytest


def _walk_source(package_name: str) -> dict[str, str]:
    """Повертає {dotted_module_name: source} для всіх .py під пакетом."""
    pkg = importlib.import_module(package_name)
    sources: dict[str, str] = {}
    for finder, name, ispkg in pkgutil.walk_packages(pkg.__path__, prefix=f"{pkg.__name__}."):
        try:
            mod = importlib.import_module(name)
            sources[name] = inspect.getsource(mod)
        except (OSError, TypeError):
            continue
    sources[pkg.__name__] = inspect.getsource(pkg)
    return sources


def test_account_module_exists_after_cutover():
    """Sanity check + skip-driver. Step 4 робить це зеленим."""
    pytest.importorskip("internal.account", reason="ще не cutover")
    importlib.import_module("internal.account")


def test_account_does_not_import_legacy_users():
    """`internal.account` НЕ повинен імпортувати `internal.users` ПІСЛЯ cleanup-коміту.

    Під час hybrid-cutover (Step 4.1-4.3) транзитивні `LegacyBacked*` адаптери
    навмисно імпортують `internal.users.*` — це branch-by-abstraction. Перевірка
    активна лише після Cleanup-коміту, який видаляє `internal/users/`.
    """
    pytest.importorskip("internal.account", reason="ще не cutover")
    try:
        importlib.import_module("internal.users")
    except ImportError:
        pass  # cleanup завершено
    else:
        pytest.skip("hybrid cutover у процесі — internal.users ще існує")
    sources = _walk_source("internal.account")
    forbidden = re.compile(r"\bfrom\s+internal\.users\b|\bimport\s+internal\.users\b")
    offenders = {name: src for name, src in sources.items() if forbidden.search(src)}
    assert not offenders, f"імпорт legacy у новому модулі: {list(offenders.keys())}"


def test_domain_does_not_import_infra_or_app():
    """Доменний шар — чистий, без знання про infra/app/ports."""
    pytest.importorskip("internal.account.domain", reason="ще не cutover")
    sources = _walk_source("internal.account.domain")
    forbidden = re.compile(
        r"\bfrom\s+internal\.account\.(infra|app|ports)\b"
        r"|\bimport\s+internal\.account\.(infra|app|ports)\b"
    )
    offenders = {name: src for name, src in sources.items() if forbidden.search(src)}
    assert not offenders, f"domain імпортує заборонене: {list(offenders.keys())}"


def test_app_does_not_import_infra():
    """App шар працює через ports, не знає про конкретні infra-адаптери."""
    pytest.importorskip("internal.account.app", reason="ще не cutover")
    sources = _walk_source("internal.account.app")
    forbidden = re.compile(
        r"\bfrom\s+internal\.account\.infra\b|\bimport\s+internal\.account\.infra\b"
    )
    offenders = {name: src for name, src in sources.items() if forbidden.search(src)}
    assert not offenders, f"app імпортує infra: {list(offenders.keys())}"


def test_ttl_lives_in_one_place_no_literal_600():
    """CRITIC.md інваріант: TTL не дублюється літералом у app-шарі."""
    pytest.importorskip("internal.account.app", reason="ще не cutover")
    sources = _walk_source("internal.account.app")
    literal = re.compile(r"\b600\b")
    offenders = {name: src for name, src in sources.items() if literal.search(src)}
    assert not offenders, (
        "літерал 600 у app-шарі — TTL мусить йти з єдиного джерела (config/domain): "
        f"{list(offenders.keys())}"
    )
