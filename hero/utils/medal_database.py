from sqlite3 import connect, Connection, Cursor
from os import path
from typing import List


db_path: str = "databases/server.db"


def init_db() -> Connection:
    db: Connection = connect(db_path)
    db.execute("""
        CREATE TABLE IF NOT EXISTS "medals" (
                "user"  INTEGER,
                "count" INTEGER
        );""")
    return db


def connect_to_db() -> Connection:
    if not path.exists(db_path):
        open(db_path, "w+").close()
    return init_db()


def select_count(db: Connection, user: int) -> List:
    c: Cursor = db.cursor()
    c = db.execute("SELECT count FROM medals WHERE user=?", (user,))
    rows: List = c.fetchall()
    if len(rows) == 0:
        return 0
    return rows[0][0]


def insert_count(db: Connection, user: int):
    db.execute("""
        INSERT INTO
            medals (user, count)
        VALUES
            (?, ?)
    """, (user, 1))
    db.commit()


def update_count(db: Connection, user: int, c: int):
    db.execute("UPDATE medals SET count=? WHERE user=?", (c, user))
    db.commit()


def select_all(db: Connection) -> List:
    c: Cursor = db.cursor()
    c = db.execute("SELECT * FROM medals")
    rows: List = c.fetchall()
    counts: dict = {}

    for row in rows[0:10]:
        counts[row[0]] = row[1]

    counts = {k: v for k, v in sorted(
        counts.items(), key=lambda item: item[1], reverse=True)}

    return counts


def user_exists(db: Connection, user: int) -> List:
    c: Cursor = db.cursor()
    c = db.execute("SELECT user FROM medals")
    rows: List = c.fetchall()
    for row in rows:
        if row[0] == user:
            return True
    return False
