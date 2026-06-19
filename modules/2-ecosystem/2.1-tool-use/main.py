"""Basic tool use demo for Module 2.

Defines two tools (get_weather, calculator), shows the tool_use → tool_result
cycle with Claude.
"""
import os
import sys

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

MODEL = "claude-sonnet-4-6"

TOOLS = [
    {
        "name": "get_weather",
        "description": "Get current weather for a city. Returns a fake but plausible value.",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City name in English"},
            },
            "required": ["city"],
        },
    },
    {
        "name": "calculator",
        "description": "Evaluate a basic arithmetic expression like '2 + 2' or '15 * 7'.",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Arithmetic expression to evaluate",
                },
            },
            "required": ["expression"],
        },
    },
]

FAKE_WEATHER = {
    "kyiv": {"temp_c": 12, "condition": "cloudy"},
    "lviv": {"temp_c": 9, "condition": "rainy"},
    "lisbon": {"temp_c": 18, "condition": "sunny"},
}


def execute_tool(name: str, args: dict) -> str:
    if name == "get_weather":
        city = args["city"].strip().lower()
        data = FAKE_WEATHER.get(city, {"temp_c": 20, "condition": "unknown"})
        return f"{city}: {data['temp_c']}°C, {data['condition']}"
    if name == "calculator":
        expr = args["expression"]
        if not all(c in "0123456789+-*/(). " for c in expr):
            return "Error: only digits and + - * / ( ) allowed"
        try:
            return str(eval(expr, {"__builtins__": {}}, {}))
        except Exception as exc:
            return f"Error: {exc}"
    return f"Unknown tool: {name}"


def run_query(client: Anthropic, question: str) -> None:
    print(f"\n=== Question: {question}")
    messages = [{"role": "user", "content": question}]

    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        tools=TOOLS,
        messages=messages,
    )

    while response.stop_reason == "tool_use":
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                print(f"  → Claude calls {block.name}({block.input})")
                result = execute_tool(block.name, block.input)
                print(f"  ← We return: {result}")
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    }
                )

        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": tool_results})

        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            tools=TOOLS,
            messages=messages,
        )

    text = "".join(block.text for block in response.content if block.type == "text")
    print(f"  Final answer: {text}")


def main() -> None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print(
            "ANTHROPIC_API_KEY not set. Copy .env.example to .env and add your key.",
            file=sys.stderr,
        )
        sys.exit(1)

    client = Anthropic()
    run_query(client, "What's the weather in Kyiv right now?")
    run_query(client, "What is 23 * 17 + 5?")


if __name__ == "__main__":
    main()
