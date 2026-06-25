"""A small task with several valid solutions — fuel for the agent-vs-agent demo.

Screencast #5 hands the SAME task below to two agents in two worktrees, then
compares the two finished results and keeps the better one. The task is chosen
on purpose so that more than one implementation is correct: there is no single
"right" layout, which is exactly when comparison beats raw parallelism.
"""


def render_card(title, items):
    """Render a text "card": a title plus a bulleted list of items.

    TASK (for the demo): implement this so it returns a nice, readable card
    as a single string. Several layouts are valid — a boxed card, an indented
    list, an aligned table. Pick one and make it clean. Two agents given this
    same task will produce different but equally correct cards; that is the
    point of the comparison.
    """
    raise NotImplementedError("render_card is the agent-vs-agent task")


if __name__ == "__main__":
    print(render_card("Release 2.4", ["auth refresh", "pagination fix", "new orders API"]))
