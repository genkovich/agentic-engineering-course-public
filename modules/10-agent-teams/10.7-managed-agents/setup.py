"""Крок 0: створити hosted code-reviewer і cloud-оточення один раз.

Створює:
  - Agent  - versioned конфіг рев'юера (модель + system + agent_toolset).
  - Environment - cloud sandbox (Ubuntu 22.04, мережа вимкнена за замовчуванням).
Зберігає AGENT_ID / ENV_ID у .env, щоб решта скриптів їх переюзали.

Ідемпотентність: щоразу створює НОВИЙ агент/оточення і перезаписує .env.
Це платний ресурс на боці Anthropic - не ганяй у циклі.
"""

from common import client, save_ids

REVIEWER_SYSTEM = (
    "Ти прискіпливий код-рев'юер. Твоя робота - знаходити помилки коректності, "
    "а не хвалити код. Особлива увага до грошової математики, округлень і "
    "крайових випадків. Для кожної знахідки: файл, рядок, чому це баг, як "
    "полагодити. Зелені тести - не доказ відсутності бага."
)


def main() -> None:
    agent = client.beta.agents.create(
        name="Course Code Reviewer",
        model="claude-opus-4-8",
        system=REVIEWER_SYSTEM,
        tools=[{"type": "agent_toolset_20260401"}],
    )
    print(f"Agent ID: {agent.id}, version: {agent.version}")

    environment = client.beta.environments.create(
        name="reviewer-cloud",
        config={
            "type": "cloud",
            "networking": {"type": "unrestricted"},
        },
    )
    print(f"Environment ID: {environment.id}")

    save_ids(agent.id, environment.id)


if __name__ == "__main__":
    main()
