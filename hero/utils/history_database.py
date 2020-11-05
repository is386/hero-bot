from sqlite3 import connect, Connection, Cursor
from os import path
from typing import List

db_path: str = "databases/server.db"


# Initializes the server database with the medals table
def init_db() -> Connection:
    db: Connection = connect(db_path)
    db.execute("""
        CREATE TABLE IF NOT EXISTS "history" (
                "id"    INTEGER NOT NULL UNIQUE,
                "user"  INTEGER,
                "infraction"  TEXT,
                "reason"      TEXT,
                "date"       DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY("id")
        );""")
    return db


# Returns a connection to the server db
def connect_to_db() -> Connection:
    if not path.exists(db_path):
        open(db_path, "w+").close()
    return init_db()


# Returns the medal count of a user
def select_history(db: Connection, user: int) -> List:
    c: Cursor = db.cursor()
    c = db.execute(
        "SELECT user, infraction, reason, date FROM history WHERE user=?", (user,))
    rows: List = c.fetchall()
    if len(rows) == 0:
        return 0
    return rows


# Inserts the medal count of a user
def insert_infraction(db: Connection, user: int, infraction: str, reason: str):
    db.execute("""
        INSERT INTO
            history (user, infraction, reason)
        VALUES
            (?, ?, ?)
    """, (user, infraction, reason))
    db.commit()
