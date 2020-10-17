from sqlite3 import connect, Connection, Cursor
from typing import List
from hero.utils.embed_model import EmbedModel


def connect_to_cmd_db() -> Connection:
    return connect("databases/commands.db")


def select_all_cmds(db: Connection) -> List:
    c: Cursor = db.cursor()
    c = db.execute("SELECT name FROM all_commands")
    rows: List = c.fetchall()
    return [row[0] for row in rows]


def select_all_text_cmds(db: Connection) -> List:
    c: Cursor = db.cursor()
    c = db.execute("SELECT name FROM all_commands WHERE type='text'")
    rows: List = c.fetchall()
    return [row[0] for row in rows]


def select_all_embed_cmds(db: Connection) -> List:
    c: Cursor = db.cursor()
    c = db.execute("SELECT name FROM all_commands WHERE type='embed'")
    rows: List = c.fetchall()
    return [row[0] for row in rows]


def select_all_custom_cmds(db: Connection) -> List:
    c: Cursor = db.cursor()
    c = db.execute("SELECT name FROM all_commands WHERE category='Custom'")
    rows: List = c.fetchall()
    return [row[0] for row in rows]


def select_all_categories(db: Connection) -> List:
    c: Cursor = db.cursor()
    c = db.execute("SELECT category FROM all_commands")
    rows: List = c.fetchall()
    return [row[0] for row in rows]


def select_cmds_in_category(category: str, db: Connection) -> List:
    c: Cursor = db.cursor()
    c = db.execute(
        "SELECT name FROM all_commands WHERE category=?", (category,))
    rows: List = c.fetchall()
    return [row[0] for row in rows]


def select_cmd_info(cmd: str, db: Connection) -> tuple:
    c: Cursor = db.cursor()
    c = db.execute(
        "SELECT description, usage, example FROM all_commands WHERE name=?", (cmd,))
    rows: List = c.fetchall()
    return rows[0]


def select_text_cmd(cmd: str, db: Connection) -> str:
    c: Cursor = db.cursor()
    c = db.execute("""
        SELECT
            id, cmd_id, name, text
        FROM
            all_commands, text_commands
        WHERE
            id = cmd_id
        AND
            name = ?
    """, (cmd,))
    return c.fetchall()[0][-1]


def select_embed_cmd(cmd: str, db: Connection) -> List:
    c: Cursor = db.cursor()
    c = db.execute("""
        SELECT
            id, cmd_id, title, embed_commands.description, footer, thumbnail, image
        FROM
            all_commands, embed_commands
        WHERE
            id = cmd_id
        AND
            name = ?
    """, (cmd,))
    rows: List = c.fetchall()
    fields: dict = select_embed_fields(rows[0][0], db)
    embedData: List = list(rows[0][2:])
    embedData.append(fields)
    return embedData


def select_embed_fields(cmd_id: int, db: Connection) -> dict:
    c: Cursor = db.cursor()
    c = db.execute(
        "SELECT name, value FROM embed_fields WHERE embed_id=?", (cmd_id,))
    rows: List = c.fetchall()
    fields: dict = {}

    for row in rows:
        fields[row[0]] = row[1]

    return fields


def select_cmd_id(cmd: str, db: Connection):
    c: Cursor = db.cursor()
    c = db.execute("SELECT id FROM all_commands WHERE name=?", (cmd,))
    return c.fetchall()[0][0]


def insert_text_cmd(cmd: str, text: str, db: Connection):
    db.execute("""
        INSERT INTO
            all_commands (name, type, category)
        VALUES
            (?, 'text', 'Custom')
    """, (cmd,))
    db.commit()

    cmd_id: int = select_cmd_id(cmd, db)

    db.execute("""
        INSERT INTO
            text_commands (cmd_id, text)
        VALUES
            (?, ?)
    """, (cmd_id, text))
    db.commit()


def update_text_cmd(cmd: str, text: str, db: Connection):
    cmd_id: int = select_cmd_id(cmd, db)
    db.execute("UPDATE text_commands SET text=? WHERE cmd_id=?", (text, cmd_id))
    db.commit()


def remove_text_cmd(cmd: str, db: Connection):
    cmd_id: int = select_cmd_id(cmd, db)
    db.execute("DELETE FROM all_commands WHERE id=?", (cmd_id,))
    db.execute("DELETE FROM text_commands WHERE cmd_id=?", (cmd_id,))
    db.commit()


def insert_embed_cmd(embed: EmbedModel, db: Connection):
    db.execute("""
        INSERT INTO
            all_commands (name, type, category)
        VALUES
            (?, 'embed', 'Custom')
    """, (embed.name,))
    db.commit()

    cmd_id: int = select_cmd_id(embed.name, db)

    db.execute("""
        INSERT INTO
            embed_commands (cmd_id, title, description, footer, thumbnail, image)
        VALUES
            (?, ?, ?, ?, ?, ?)
    """, (cmd_id, embed.title, embed.description, embed.footer, embed.thumbnail, embed.image))
    db.commit()

    for f in embed.fields.keys():
        db.execute("""
            INSERT INTO
                embed_fields (embed_id, name, value)
            VALUES
                (?, ?, ?)
        """, (cmd_id, f, embed.fields[f]))
    db.commit()


def update_embed_cmd(embed: EmbedModel, db: Connection):
    cmd_id: int = select_cmd_id(embed.name, db)
    db.execute("""
        UPDATE
            embed_commands
        SET
            title=?, description=?, footer=?, thumbnail=?, image=?
        WHERE
            cmd_id=?
    """, (embed.title, embed.description, embed.footer, embed.thumbnail, embed.image, cmd_id))
    db.commit()

    for f in embed.fields.keys():
        db.execute("""
            UPDATE
                embed_fields
            SET
                name=?, value=?
            WHERE
                embed_id=?
        """, (f, embed.fields[f], cmd_id))
    db.commit()


def remove_embed_cmd(cmd: str, db: Connection):
    cmd_id: int = select_cmd_id(cmd, db)
    db.execute("DELETE FROM all_commands WHERE id=?", (cmd_id,))
    db.execute("DELETE FROM embed_commands WHERE cmd_id=?", (cmd_id,))
    db.execute("DELETE FROM embed_fields WHERE embed_id=?", (cmd_id,))
    db.commit()
