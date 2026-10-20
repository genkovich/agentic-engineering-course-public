"""Shared helpers for the count_tokens scripts: key check and readable errors."""
import os
import sys

import anthropic
from dotenv import load_dotenv

load_dotenv()


def require_api_key() -> None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print(
            "ANTHROPIC_API_KEY не задано. Скопіюй .env.example у .env і встав свій ключ "
            "з platform.claude.com.",
            file=sys.stderr,
        )
        sys.exit(1)


def make_client() -> anthropic.Anthropic:
    require_api_key()
    return anthropic.Anthropic()


def count_tokens(client: anthropic.Anthropic, model: str, text: str) -> int:
    try:
        result = client.messages.count_tokens(
            model=model,
            messages=[{"role": "user", "content": text}],
        )
    except anthropic.AuthenticationError:
        fail("Ключ не підходить (401). Перевір ANTHROPIC_API_KEY у .env.")
    except anthropic.NotFoundError:
        fail(f"Модель {model} не знайдена (404). Перевір назву або доступ акаунта до неї.")
    except anthropic.BadRequestError as err:
        if "credit balance" in str(err):
            fail(
                "API відповів «credit balance is too low». count_tokens безкоштовний, "
                "але API-акаунт на platform.claude.com має мати поповнений баланс. "
                "Підписка Pro/Max на claude.ai його не покриває: це окремий рахунок."
            )
        fail(f"API відкинув запит (400): {err.message}")
    except anthropic.APIConnectionError:
        fail("Немає з'єднання з api.anthropic.com. Перевір мережу або проксі.")
    except anthropic.APIStatusError as err:
        fail(f"API повернув {err.status_code}: {err.message}")
    return result.input_tokens


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    sys.exit(1)
