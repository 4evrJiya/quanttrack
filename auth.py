"""
Authentication Module — handles user signup, login, and password security.

Passwords are never stored in plain text. Instead, each password is combined
with a random "salt" and scrambled using a one-way hashing function (SHA-256).
This means even if the database were ever exposed, no one could read the
actual passwords back out — not even us.
"""

import sqlite3
import hashlib
import secrets


def init_users_table(db_path="quanttrack.db"):
    """Creates the users table if it doesn't already exist."""
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def hash_password(password, salt):
    """Combines the password with the salt and hashes it. Always produces the
    same output for the same password+salt, but can't be reversed back to the password."""
    return hashlib.sha256((password + salt).encode()).hexdigest()


def create_user(username, email, password, db_path="quanttrack.db"):
    """Creates a new user account. Returns (success: bool, message: str)."""
    if len(password) < 6:
        return False, "Password must be at least 6 characters long."

    init_users_table(db_path)
    conn = sqlite3.connect(db_path)

    salt = secrets.token_hex(16)  # a random string, unique per user
    password_hash = hash_password(password, salt)

    try:
        conn.execute(
            "INSERT INTO users (username, email, password_hash, salt) VALUES (?, ?, ?, ?)",
            (username, email, password_hash, salt)
        )
        conn.commit()
        return True, "Account created successfully!"
    except sqlite3.IntegrityError:
        return False, "That username or email is already taken."
    finally:
        conn.close()


def verify_user(username, password, db_path="quanttrack.db"):
    """Checks login credentials. Returns (success: bool, user_id_or_message)."""
    init_users_table(db_path)
    conn = sqlite3.connect(db_path)

    row = conn.execute(
        "SELECT user_id, password_hash, salt FROM users WHERE username = ?",
        (username,)
    ).fetchone()
    conn.close()

    if row is None:
        return False, "No account found with that username."

    user_id, stored_hash, salt = row
    attempted_hash = hash_password(password, salt)

    if attempted_hash == stored_hash:
        return True, user_id
    else:
        return False, "Incorrect password."