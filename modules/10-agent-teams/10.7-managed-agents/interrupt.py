"""Скринкаст #2: перебити рев'ю посеред роботи і перенаправити.

Той самий hosted reviewer. Стартуємо широке рев'ю, а тоді шлемо
user.interrupt + новий user.message: «облиш форматування, зосередься лише на
округленні в discount.js». Агент підтверджує і перемикає напрямок.

Тут interrupt відправляється одразу після старту заради детермінізму демо; у
житті ти шлеш його, побачивши в стрімі, що агент пішов не туди.
"""

from common import client, load_ids, review_request

REDIRECT = (
    "Стоп. Форматування і стиль не чіпай. Зосередься тільки на одному: "
    "чи коректно рахується сума в src/invoice.js та src/discount.js. "
    "Дай один найважливіший баг округлення з доказом на конкретних числах."
)


def main() -> None:
    ids = load_ids()

    session = client.beta.sessions.create(
        agent=ids["AGENT_ID"],
        environment_id=ids["ENV_ID"],
        title="Interrupt + redirect review",
    )
    print(f"Session ID: {session.id}")

    # 1. Стартуємо широке рев'ю.
    client.beta.sessions.events.send(
        session.id,
        events=[
            {
                "type": "user.message",
                "content": [{"type": "text", "text": review_request()}],
            }
        ],
    )

    # 2. Перебиваємо і перенаправляємо: interrupt + новий message одним пакетом.
    client.beta.sessions.events.send(
        session.id,
        events=[
            {"type": "user.interrupt"},
            {
                "type": "user.message",
                "content": [{"type": "text", "text": REDIRECT}],
            },
        ],
    )

    # 3. Дивимось, як агент підхоплює новий напрямок.
    with client.beta.sessions.events.stream(session.id) as stream:
        for event in stream:
            match event.type:
                case "agent.message":
                    for block in event.content:
                        if block.type == "text":
                            print(block.text, end="")
                case "agent.tool_use":
                    print(f"\n[Using tool: {event.name}]")
                case "session.status_idle":
                    print("\n\nПеренаправлене рев'ю завершено.")
                    break


if __name__ == "__main__":
    main()
