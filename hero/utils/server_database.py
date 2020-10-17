from sqlite3 import connect, Connection, Cursor
from typing import List


def connect_to_db() -> Connection:
    return connect("databases/server.db")


def select_welcome(db: Connection, server: int):
    c: Cursor = db.cursor()
    c = db.execute(
        "SELECT welcome_chan, welcome_msg FROM info WHERE id=?", (server,))
    rows: List = c.fetchall()
    if len(rows) == 0:
        return 0
    return rows[0]


def insert_welcome(db: Connection, server: int, chan: int, msg: str):
    db.execute(
        "INSERT INTO info (id, welcome_chan, welcome_msg) VALUES (?, ?, ?)", (server, chan, msg))
    db.commit()


def update_welcome(db: Connection, server: int, chan: int, msg: str):
    db.execute(
        "UPDATE info SET welcome_chan=?, welcome_msg=? WHERE id=?", (chan, msg, server))
    db.commit()
