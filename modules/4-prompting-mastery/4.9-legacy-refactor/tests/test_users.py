"""
tests/test_users.py — baseline тести.

ПОПЕРЕДЖЕННЯ: ці тести навмисно «привиди». Лекція 4.9 (Пастка 2) розбирає
саме їх як приклад того, що бачимо у legacy.

Anti-patterns тут:
1. test_register — `assert True` після виклику. Тест зелений завжди.
2. test_verify — виклик без assertion. pytest проходить, але нічого
   не перевірено.
3. test_reset — мовчазний email.send() через мок. Тест зелений, бо
   ніщо не може впасти.
4. `from internal.users import *` — приховує що саме використано.

Курсант повинен у Step 3 написати справжні тести у `tests/account/`,
а ці залишити як baseline до Step 4 (read-only).
"""
from internal.users import *      # навмисне погана імпорт-практика


def test_register():
    user = register("user@example.com", "GoodPass123")  # noqa: F405
    assert True   # ← привид! tests will always pass


def test_verify():
    verify_email("some-token")  # noqa: F405
    # без assertion — pytest вважає це успіхом


def test_reset():
    reset_password("x@y.com")   # noqa: F405
    # email.send() мовчить (1ms sleep), нічого не зламається
