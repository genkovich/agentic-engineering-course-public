"""Notifications domain events.

Notifications BC currently does not publish its own events — it is a sink
that listens to other BCs. We declare this module for future use (e.g.
``NotificationSent`` for analytics).
"""
from __future__ import annotations
