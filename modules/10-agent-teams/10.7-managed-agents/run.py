"""Скринкаст #1: hosted code-reviewer ревʼює course-репо і стрімить хід.

Мінімальний флоу поверх setup.py:
  1. створити session (agent + environment) - провізіонить sandbox, статус idle;
  2. відкрити SSE-стрім;
  3. послати user.message з рев'ю-запитом - оце й СТАРТУЄ роботу;
  4. читати events: текст агента, [Using tool: ...], зупинка по session.status_idle.

Стан сесії persisted server-side - її видно в session-viewer на platform.claude.com.
"""

from common import client, load_ids, review_request


def main() -> None:
    ids = load_ids()

    session = client.beta.sessions.create(
        agent=ids["AGENT_ID"],
        environment_id=ids["ENV_ID"],
        title="Review billing-core discount math",
    )
    print(f"Session ID: {session.id} (статус idle - чекає на user.message)")

    with client.beta.sessions.events.stream(session.id) as stream:
        # user.message шлемо ПІСЛЯ відкриття стріму; API буферизує до приєднання
        client.beta.sessions.events.send(
            session.id,
            events=[
                {
                    "type": "user.message",
                    "content": [{"type": "text", "text": review_request()}],
                }
            ],
        )

        for event in stream:
            match event.type:
                case "agent.message":
                    for block in event.content:
                        if block.type == "text":
                            print(block.text, end="")
                case "agent.tool_use":
                    print(f"\n[Using tool: {event.name}]")
                case "session.status_idle":
                    print("\n\nРев'ю завершено.")
                    break


if __name__ == "__main__":
    main()
