"""Domain errors for the notes library."""


class NotesError(Exception):
    """Raised when a notes operation fails in an expected way.

    Use this for misses a caller can reasonably handle — a missing note id,
    a missing title — instead of letting a bare ``KeyError`` or
    ``StopIteration`` escape. Always carry a message that names what was
    missing.
    """
