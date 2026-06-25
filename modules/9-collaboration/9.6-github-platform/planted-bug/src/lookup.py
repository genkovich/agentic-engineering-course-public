"""User lookup by email.

PLANTED BUG (for the reviewers to catch): `find_user` builds the SQL query by
string-concatenating unsanitised user input — a textbook SQL injection. An
email like  ' OR '1'='1  returns every row; a crafted payload can drop tables.

Fix the reviewers should suggest: a parameterised query —
    cur.execute("SELECT id, email FROM users WHERE email = ?", (email,))
"""

import sqlite3


def find_user(conn: sqlite3.Connection, email: str):
    """Return the user row matching `email`, or None."""
    cur = conn.cursor()
    # BUG: unsanitised `email` interpolated straight into the SQL string.
    query = "SELECT id, email FROM users WHERE email = '" + email + "'"
    cur.execute(query)
    return cur.fetchone()
