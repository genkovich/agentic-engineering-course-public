"""Agentic loop demo for Module 2.

Explicit observe → think → act loop with multiple tools, no SDK helpers.
The agent explores a fake filesystem to answer a question.
"""
import os
import sys

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

MODEL = "claude-sonnet-4-6"
MAX_ITERATIONS = 8

FAKE_FS = {
    "/project/README.md": "Project alpha. See docs/ for setup. License: MIT.",
    "/project/docs/setup.md": "Run `make install`. Requires Python 3.10+ and DATABASE_URL.",
    "/project/docs/architecture.md": "Three layers: API, service, repo. See ADR-001.",
    "/project/src/main.py": "from fastapi import FastAPI\napp = FastAPI()",
    "/project/src/db.py": "DATABASE_URL = 'postgres://localhost:5432/alpha'",
    "/project/.env.example": "DATABASE_URL=\nSECRET_KEY=",
}

TOOLS = [
    {
        "name": "list_files",
        "description": "List files under a directory path. Returns one path per line.",
        "input_schema": {
            "type": "object",
            "properties": {
                "directory": {"type": "string", "description": "Directory path"},
            },
            "required": ["directory"],
        },
    },
    {
        "name": "read_file",
        "description": "Read the contents of a file at the given absolute path.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Absolute file path"},
            },
            "required": ["path"],
        },
    },
    {
        "name": "grep",
        "description": "Search for a substring across all files. Returns matching paths.",
        "input_schema": {
            "type": "object",
            "properties": {
                "pattern": {"type": "string", "description": "Substring to search"},
            },
            "required": ["pattern"],
        },
    },
]


def execute_tool(name: str, args: dict) -> str:
    if name == "list_files":
        prefix = args["directory"].rstrip("/") + "/"
        matches = [p for p in FAKE_FS if p.startswith(prefix)]
        return "\n".join(matches) if matches else "(empty)"
    if name == "read_file":
        return FAKE_FS.get(args["path"], f"Error: {args['path']} not found")
    if name == "grep":
        pattern = args["pattern"]
        matches = [p for p, content in FAKE_FS.items() if pattern in content]
        return "\n".join(matches) if matches else "(no matches)"
    return f"Unknown tool: {name}"


def main() -> None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print(
            "ANTHROPIC_API_KEY not set. Copy .env.example to .env and add your key.",
            file=sys.stderr,
        )
        sys.exit(1)

    client = Anthropic()
    question = (
        "What database does this project use, and where is it configured? "
        "You have list_files, read_file, and grep tools. Start at /project."
    )
    messages = [{"role": "user", "content": question}]

    print(f"=== Question: {question}\n")

    for iteration in range(1, MAX_ITERATIONS + 1):
        print(f"--- Iteration {iteration} ---")
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            tools=TOOLS,
            messages=messages,
        )

        for block in response.content:
            if block.type == "text" and block.text.strip():
                print(f"  [think] {block.text.strip()}")
            elif block.type == "tool_use":
                print(f"  [act]   {block.name}({block.input})")

        if response.stop_reason != "tool_use":
            text = "".join(b.text for b in response.content if b.type == "text")
            print(f"\n=== Final answer ===\n{text}")
            print(f"\nLoop terminated after {iteration} iterations.")
            return

        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                result = execute_tool(block.name, block.input)
                preview = result.replace("\n", " | ")[:120]
                print(f"  [obs]   {preview}")
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    }
                )

        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": tool_results})

    print(f"\nReached max iterations ({MAX_ITERATIONS}) without final answer.")


if __name__ == "__main__":
    main()
