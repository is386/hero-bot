from sqlite3 import connect, Connection, Cursor
from os import path
from typing import List
from hero.utils.embed_model import EmbedModel

db_path: str = "databases/commands.db"


# Initalizes the db with the necessary tables
def init_db() -> Connection:
    db: Connection = connect(db_path)
    db.execute("""
        CREATE TABLE IF NOT EXISTS "embed_fields" (
                "embed_id"      INTEGER,
                "name"  TEXT,
                "value" TEXT
        );""")
    db.execute("""
        CREATE TABLE IF NOT EXISTS "text_commands" (
                "cmd_id"        INTEGER,
                "text"  TEXT
        );""")
    db.execute("""
        CREATE TABLE IF NOT EXISTS "embed_commands" (
                "cmd_id"        INTEGER,
                "title" TEXT,
                "description"   TEXT,
                "footer"        TEXT,
                "thumbnail"     TEXT,
                "image" TEXT
        );""")
    db.execute("""
        CREATE TABLE IF NOT EXISTS "all_commands" (
                "id"    INTEGER NOT NULL UNIQUE,
                "name"  TEXT UNIQUE,
                "type"  TEXT,
                "category"      TEXT,
                "aliases"       TEXT,
                "description"   TEXT,
                "usage" TEXT,
                "example"       TEXT,
                PRIMARY KEY("id")
        ); """)
    return db


# Returns a connection to the cmd db
def connect_to_cmd_db() -> Connection:
    if not path.exists(db_path):
        open(db_path, "w+").close()
    return init_db()


# Returns a list of every command's name
def select_all_cmds(db: Connection) -> List:
    c: Cursor = db.cursor()
    c = db.execute("SELECT name FROM all_commands")
    rows: List = c.fetchall()
    return [row[0] for row in rows]


# Returns a list of every text command's name
def select_all_text_cmds(db: Connection) -> List:
    c: Cursor = db.cursor()
    c = db.execute("SELECT name FROM all_commands WHERE type='text'")
    rows: List = c.fetchall()
    return [row[0] for row in rows]


# Returns a list of every embed command's name
def select_all_embed_cmds(db: Connection) -> List:
    c: Cursor = db.cursor()
    c = db.execute("SELECT name FROM all_commands WHERE type='embed'")
    rows: List = c.fetchall()
    return [row[0] for row in rows]


# Returns a list of every custom command's name
def select_all_custom_cmds(db: Connection) -> List:
    c: Cursor = db.cursor()
    c = db.execute("SELECT name FROM all_commands WHERE category='Custom'")
    rows: List = c.fetchall()
    return [row[0] for row in rows]


# Returns a list of every command category
def select_all_categories(db: Connection) -> List:
    c: Cursor = db.cursor()
    c = db.execute("SELECT category FROM all_commands")
    rows: List = c.fetchall()
    return [row[0] for row in rows]


# Returns a list of all the command names within a specific category
def select_cmds_in_category(category: str, db: Connection) -> List:
    c: Cursor = db.cursor()
    c = db.execute(
        "SELECT name FROM all_commands WHERE category=?", (category,))
    rows: List = c.fetchall()
    return [row[0] for row in rows]


# Returns the description, usage, and examples for a specific command
def select_cmd_info(cmd: str, db: Connection) -> tuple:
    c: Cursor = db.cursor()
    c = db.execute(
        "SELECT description, usage, example FROM all_commands WHERE name=?", (cmd,))
    rows: List = c.fetchall()
    return rows[0]


# Returns the id, cmd_id, and text of a text command
def select_text_cmd(cmd: str, db: Connection) -> str:
    c: Cursor = db.cursor()
    c = db.execute("""
        SELECT
            id, cmd_id, name, text
        FROM
            all_commands, text_commands
        WHERE
            id=cmd_id
        AND
            name= ?
    """, (cmd,))
    return c.fetchall()[0][-1]


# Returns the id, cmd_id, and all parts of an embed
def select_embed_cmd(cmd: str, db: Connection) -> List:
    c: Cursor = db.cursor()
    c = db.execute("""
        SELECT
            id, cmd_id, title, embed_commands.description, footer, thumbnail, image
        FROM
            all_commands, embed_commands
        WHERE
            id=cmd_id
        AND
            name= ?
    """, (cmd,))
    rows: List = c.fetchall()
    fields: dict = select_embed_fields(rows[0][0], db)
    embedData: List = list(rows[0][2:])
    embedData.append(fields)
    return embedData


# Selects the fields of a specified embed by its id
def select_embed_fields(cmd_id: int, db: Connection) -> dict:
    c: Cursor = db.cursor()
    c = db.execute(
        "SELECT name, value FROM embed_fields WHERE embed_id=?", (cmd_id,))
    rows: List = c.fetchall()
    fields: dict = {}

    for row in rows:
        fields[row[0]] = row[1]

    return fields


# Returns the id of a command in the db
def select_cmd_id(cmd: str, db: Connection):
    c: Cursor = db.cursor()
    c = db.execute("SELECT id FROM all_commands WHERE name=?", (cmd,))
    return c.fetchall()[0][0]


# Inserts a text command given its name and text
def insert_text_cmd(cmd: str, text: str, db: Connection):
    db.execute("""
        INSERT INTO
            all_commands(name, type, category)
        VALUES
            (?, 'text', 'Custom')
    """, (cmd,))
    db.commit()

    cmd_id: int = select_cmd_id(cmd, db)

    db.execute("""
        INSERT INTO
            text_commands(cmd_id, text)
        VALUES
            (?, ?)
    """, (cmd_id, text))
    db.commit()


# Updates a text command given its name and text
def update_text_cmd(cmd: str, text: str, db: Connection):
    cmd_id: int = select_cmd_id(cmd, db)
    db.execute("UPDATE text_commands SET text=? WHERE cmd_id=?", (text, cmd_id))
    db.commit()


# Removes a text command given its name
def remove_text_cmd(cmd: str, db: Connection):
    cmd_id: int = select_cmd_id(cmd, db)
    db.execute("DELETE FROM all_commands WHERE id=?", (cmd_id,))
    db.execute("DELETE FROM text_commands WHERE cmd_id=?", (cmd_id,))
    db.commit()


# Inserts an embed command given its embed model
def insert_embed_cmd(embed: EmbedModel, db: Connection):
    db.execute("""
        INSERT INTO
            all_commands(name, type, category)
        VALUES
            (?, 'embed', 'Custom')
    """, (embed.name,))
    db.commit()

    cmd_id: int = select_cmd_id(embed.name, db)

    db.execute("""
        INSERT INTO
            embed_commands(cmd_id, title, description,
                           footer, thumbnail, image)
        VALUES
            (?, ?, ?, ?, ?, ?)
    """, (cmd_id, embed.title, embed.description, embed.footer, embed.thumbnail, embed.image))
    db.commit()

    # Inserts the fields of the embed into a separate table
    for f in embed.fields.keys():
        db.execute("""
            INSERT INTO
                embed_fields(embed_id, name, value)
            VALUES
                (?, ?, ?)
        """, (cmd_id, f, embed.fields[f]))
    db.commit()


# Updates an embed command given its embed model
def update_embed_cmd(embed: EmbedModel, db: Connection):
    cmd_id: int = select_cmd_id(embed.name, db)
    if embed.title:
        db.execute(
            """UPDATE embed_commands SET title=? WHERE cmd_id=?""", (embed.title, cmd_id))
        db.commit()
    if embed.description:
        db.execute(
            """UPDATE embed_commands SET description=? WHERE cmd_id=?""", (embed.description, cmd_id))
        db.commit()
    if embed.footer:
        db.execute(
            """UPDATE embed_commands SET footer=? WHERE cmd_id=?""", (embed.footer, cmd_id))
        db.commit()
    if embed.thumbnail:
        db.execute(
            """UPDATE embed_commands SET thumbnail=? WHERE cmd_id=?""", (embed.thumbnail, cmd_id))
        db.commit()
    if embed.image:
        db.execute(
            """UPDATE embed_commands SET image=? WHERE cmd_id=?""", (embed.image, cmd_id))
        db.commit()

    # Fields that currently exist for this command
    fields: dict = select_embed_fields(cmd_id, db)

    # Updates the fields of the embed into a separate table
    for f in embed.fields.keys():
        # If the field exists, update, else insert it because its a new field
        if f in fields.keys():
            db.execute("""UPDATE embed_fields SET name=?, value=? WHERE embed_id=? AND name=?""",
                       (f, embed.fields[f], cmd_id, f))
        else:
            db.execute("""INSERT INTO embed_fields(embed_id, name, value) VALUES (?, ?, ?) """,
                       (cmd_id, f, embed.fields[f]))
        db.commit()


# Removes an embed command and its fields from the db
def remove_embed_cmd(cmd: str, db: Connection):
    cmd_id: int = select_cmd_id(cmd, db)
    db.execute("DELETE FROM all_commands WHERE id=?", (cmd_id,))
    db.execute("DELETE FROM embed_commands WHERE cmd_id=?", (cmd_id,))
    db.execute("DELETE FROM embed_fields WHERE embed_id=?", (cmd_id,))
    db.commit()
