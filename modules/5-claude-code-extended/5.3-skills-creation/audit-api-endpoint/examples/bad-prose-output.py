#!/usr/bin/env python3
"""Bad pattern: human-friendly ASCII table mixed with diagnostic warnings
on the same stream. The agent has to grep this with regex, and updates
to the table format break every consumer.
"""

print("===========================================")
print(" Audit results for /health")
print("===========================================")
print(" WARNING: server not responding, using static analysis only")
print(" 1. observability   no log call         api/server.go:32")
print(" 2. health          uptime-only check   api/server.go:35")
print("===========================================")
print(" 2 findings - run with --verbose for details")
