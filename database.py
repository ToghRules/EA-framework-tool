"""
Database Module — SQLite
Handles all database operations:
  - User accounts (register / login)
  - Saved scenarios per user
  - Evaluation results history per user

Tables
------
    users           → id, username, email, password_hash, created_at
    scenarios       → id, user_id, name, frameworks, weights, created_at
    eval_results    → id, user_id, scenario_name, framework, score, weights_snapshot, created_at
"""

import sqlite3
import hashlib
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "ea_tool.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row          
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create all tables if they don't exist. Safe to call on every startup."""
    conn = get_connection()
    cur = conn.cursor()

    cur.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            username      TEXT    NOT NULL UNIQUE,
            email         TEXT    NOT NULL UNIQUE,
            password_hash TEXT    NOT NULL,
            created_at    TEXT    NOT NULL
        );

        CREATE TABLE IF NOT EXISTS scenarios (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            name        TEXT    NOT NULL,
            frameworks  TEXT    NOT NULL,   -- JSON list
            weights     TEXT    NOT NULL,   -- JSON dict
            created_at  TEXT    NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE(user_id, name)
        );

        CREATE TABLE IF NOT EXISTS eval_results (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id           INTEGER NOT NULL,
            session_label     TEXT    NOT NULL,
            results_json      TEXT    NOT NULL,   -- full results dict as JSON
            weights_snapshot  TEXT    NOT NULL,   -- weights used
            frameworks        TEXT    NOT NULL,   -- frameworks evaluated
            winner            TEXT    NOT NULL,
            winner_score      REAL    NOT NULL,
            created_at        TEXT    NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
    """)

    conn.commit()
    conn.close()


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def register_user(username: str, email: str, password: str) -> tuple[bool, str]:
    """
    Register a new user.
    Returns (success: bool, message: str)
    """
    if len(username.strip()) < 3:
        return False, "Username must be at least 3 characters."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    if "@" not in email:
        return False, "Please enter a valid email address."

    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO users (username, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
            (username.strip(), email.strip().lower(), _hash_password(password), _now())
        )
        conn.commit()
        return True, "Account created successfully!"
    except sqlite3.IntegrityError as e:
        if "username" in str(e):
            return False, "Username already taken."
        if "email" in str(e):
            return False, "An account with this email already exists."
        return False, "Registration failed."
    finally:
        conn.close()


def login_user(username: str, password: str) -> tuple[bool, dict | None, str]:
    """
    Authenticate a user.
    Returns (success, user_row_dict | None, message)
    """
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM users WHERE username = ? AND password_hash = ?",
            (username.strip(), _hash_password(password))
        ).fetchone()
        if row:
            return True, dict(row), "Login successful."
        return False, None, "Invalid username or password."
    finally:
        conn.close()


def get_user_by_id(user_id: int) -> dict | None:
    conn = get_connection()
    try:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()



def save_scenario(user_id: int, name: str, frameworks: list, weights: dict) -> tuple[bool, str]:
    """Save or overwrite a scenario for a user."""
    conn = get_connection()
    try:
        
        conn.execute(
            "DELETE FROM scenarios WHERE user_id = ? AND name = ?",
            (user_id, name)
        )
        conn.execute(
            "INSERT INTO scenarios (user_id, name, frameworks, weights, created_at) VALUES (?, ?, ?, ?, ?)",
            (user_id, name, json.dumps(frameworks), json.dumps(weights), _now())
        )
        conn.commit()
        return True, f'Scenario "{name}" saved.'
    except Exception as e:
        return False, f"Failed to save scenario: {e}"
    finally:
        conn.close()


def load_scenarios(user_id: int) -> list[dict]:
    """Return all scenarios for a user as a list of dicts."""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM scenarios WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,)
        ).fetchall()
        result = []
        for row in rows:
            d = dict(row)
            d["frameworks"] = json.loads(d["frameworks"])
            d["weights"]    = json.loads(d["weights"])
            result.append(d)
        return result
    finally:
        conn.close()


def delete_scenario(user_id: int, scenario_id: int) -> tuple[bool, str]:
    conn = get_connection()
    try:
        conn.execute(
            "DELETE FROM scenarios WHERE id = ? AND user_id = ?",
            (scenario_id, user_id)
        )
        conn.commit()
        return True, "Scenario deleted."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()



def save_eval_result(
    user_id: int,
    session_label: str,
    results: dict,
    weights: dict,
    frameworks: list,
) -> tuple[bool, str]:
    """Persist a full evaluation result to history."""
    sorted_results = sorted(results.items(), key=lambda x: x[1]["final_score"], reverse=True)
    winner     = sorted_results[0][0]
    winner_score = sorted_results[0][1]["final_score"]

    
    storable = {
        fw: {
            "final_score":     float(data["final_score"]),
            "top_criteria":    data["top_criteria"],
            "weighted_scores": {k: float(v) for k, v in data["weighted_scores"].items()},
            "raw_scores":      {k: float(v) for k, v in data["raw_scores"].items()},
        }
        for fw, data in results.items()
    }

    conn = get_connection()
    try:
        conn.execute(
            """INSERT INTO eval_results
               (user_id, session_label, results_json, weights_snapshot, frameworks, winner, winner_score, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                user_id,
                session_label,
                json.dumps(storable),
                json.dumps({k: int(v) for k, v in weights.items()}),
                json.dumps(frameworks),
                winner,
                winner_score,
                _now(),
            )
        )
        conn.commit()
        return True, "Evaluation saved to history."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()


def load_eval_history(user_id: int, limit: int = 50) -> list[dict]:
    """Return recent evaluation history for a user."""
    conn = get_connection()
    try:
        rows = conn.execute(
            """SELECT * FROM eval_results
               WHERE user_id = ?
               ORDER BY created_at DESC
               LIMIT ?""",
            (user_id, limit)
        ).fetchall()
        result = []
        for row in rows:
            d = dict(row)
            d["results_json"]     = json.loads(d["results_json"])
            d["weights_snapshot"] = json.loads(d["weights_snapshot"])
            d["frameworks"]       = json.loads(d["frameworks"])
            result.append(d)
        return result
    finally:
        conn.close()


def delete_eval_result(user_id: int, result_id: int) -> tuple[bool, str]:
    conn = get_connection()
    try:
        conn.execute(
            "DELETE FROM eval_results WHERE id = ? AND user_id = ?",
            (result_id, user_id)
        )
        conn.commit()
        return True, "Record deleted."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()



def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
