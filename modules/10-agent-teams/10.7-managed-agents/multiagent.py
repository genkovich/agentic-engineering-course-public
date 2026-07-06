"""Скринкаст #4 (КЛІМАКС #2): координатор розкидає рев'ю на треди bug/test/docs.

Три спеціалізовані агенти + один координатор із роль-ростером (`multiagent`).
В одній сесії координатор делегує роботу в context-isolated session threads:
спільний sandbox, але окремі контексти й тули на кожного. API-аналог Agent
Teams з 10.4, але вбудований в один Managed-Agents-сеанс.

Дзеркалить codereview-плагін: bug-detector / test-coverage / docs-compliance.
"""

from common import client, load_ids, review_request

SPECIALISTS = {
    "bug": "Ти шукаєш лише помилки коректності: округлення, крайові випадки, грошова математика.",
    "test": "Ти шукаєш пробіли в тестах: які шляхи не покриті, які кейси пройдуть повз зелений suite.",
    "docs": "Ти звіряєш коментарі й README з кодом: де опис розходиться з поведінкою.",
}


def main() -> None:
    ids = load_ids()

    # 1. Три спеціалісти - кожен окремий versioned агент.
    roster = []
    for key, system in SPECIALISTS.items():
        agent = client.beta.agents.create(
            name=f"reviewer-{key}",
            model="claude-opus-4-8",
            system=system,
            tools=[{"type": "agent_toolset_20260401"}],
        )
        print(f"{key}: {agent.id}")
        roster.append({"type": "agent", "id": agent.id})

    # 2. Координатор із роль-ростером у полі multiagent.
    coordinator = client.beta.agents.create(
        name="review-coordinator",
        model="claude-opus-4-8",
        system=(
            "Ти координуєш код-рев'ю. Делегуй пошук багів агенту reviewer-bug, "
            "пробіли в тестах - reviewer-test, розбіжності в документації - "
            "reviewer-docs. Збери їхні висновки в один звіт."
        ),
        tools=[{"type": "agent_toolset_20260401"}],
        multiagent={"type": "coordinator", "agents": roster},
    )
    print(f"coordinator: {coordinator.id}")

    # 3. Сесія на координаторі; primary thread = стрім координатора,
    #    треди спеціалістів спавняться, коли він делегує.
    session = client.beta.sessions.create(
        agent=coordinator.id,
        environment_id=ids["ENV_ID"],
        title="Multi-agent review: bug / test / docs",
    )
    print(f"Session ID: {session.id}")

    with client.beta.sessions.events.stream(session.id) as stream:
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
                case "session.thread_created":
                    print("\n[тред спеціаліста створено]")
                case "agent.thread_message_received":
                    print("\n[спеціаліст повернув результат координатору]")
                case "session.status_idle":
                    print("\n\nЗведене рев'ю готове.")
                    break


if __name__ == "__main__":
    main()
