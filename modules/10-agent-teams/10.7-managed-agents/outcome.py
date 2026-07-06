"""Скринкаст #3 (КЛІМАКС #1): define-outcome + рубрика -> grader судить рев'ю.

Замість «пройдися по коду» ми задаємо ВИХІД: «рев'ю мусить спіймати баг
округлення». Harness авто-провізіонить grader в ОКРЕМОМУ контекстному вікні,
ганяє артефакт рев'ю по rubric.md, повертає фідбек агенту - той ітерує, поки
критерії не виконані. Дзеркало Evaluator-а з 10.6, тільки зібраний за тебе.

user.define_outcome стартує роботу сам - додатковий user.message не потрібен.
"""

from pathlib import Path

from common import client, load_ids, review_request

RUBRIC = Path(__file__).resolve().parent.joinpath("rubric.md").read_text()


def main() -> None:
    ids = load_ids()

    session = client.beta.sessions.create(
        agent=ids["AGENT_ID"],
        environment_id=ids["ENV_ID"],
        title="Outcome: review must catch the seeded bug",
    )
    print(f"Session ID: {session.id}")

    client.beta.sessions.events.send(
        session.id,
        events=[
            {
                "type": "user.define_outcome",
                "description": (
                    "Дай код-рев'ю модуля рахунків, яке ловить баг подвійного "
                    "округлення в грошовій математиці. Ось код:\n\n"
                    + review_request()
                ),
                "rubric": {"type": "text", "content": RUBRIC},
                "max_iterations": 5,  # опційно; дефолт 3, максимум 20
            }
        ],
    )

    with client.beta.sessions.events.stream(session.id) as stream:
        for event in stream:
            match event.type:
                case "agent.message":
                    for block in event.content:
                        if block.type == "text":
                            print(block.text, end="")
                case "agent.tool_use":
                    print(f"\n[Using tool: {event.name}]")
                case "span.outcome_evaluation_start":
                    print("\n[grader оцінює рев'ю проти рубрики...]")
                case "span.outcome_evaluation_end":
                    print("\n[grader повернув вердикт агенту]")
                case "session.status_idle":
                    print("\n\nКритерії рубрики виконані.")
                    break


if __name__ == "__main__":
    main()
