#!/usr/bin/env python3
"""Bad pattern: interactive prompt inside a script the agent will call.

Run this and notice the script blocks waiting for input. An agent that
calls it has no TTY, so the read() never returns and the whole skill run
hangs until the harness times out. There is no exit code, no error,
just silence.
"""
target = input("Enter target path: ")
endpoint = input("Enter endpoint: ")
print(f"would audit {endpoint} in {target}")
