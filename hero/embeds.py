from typing import List
from sqlite3 import Connection

from discord import Embed
from hero import cmd_database, meme, url
from hero.embed_model import EmbedModel

embed_color = 16765210


def create_embed(embedModel: EmbedModel):
    embed: Embed = Embed(title=embedModel.title,
                         color=embed_color, description=embedModel.description)

    if embedModel.footer is not None:
        embed.set_footer(text=embedModel.footer)

    if embedModel.thumbnail is not None:
        embed.set_thumbnail(url=embedModel.thumbnail)

    if embedModel.image is not None:
        embed.set_image(url=embedModel.image)

    if embedModel.fields is not None:
        for i in embedModel.fields.keys():
            embed.add_field(name=i, value=embedModel.fields[i], inline=False)

    return embed


def get_embed_model(cmd: str):
    cmd_db: Connection = cmd_database.connect_to_cmd_db()
    embedData: List = cmd_database.select_embed_cmd(cmd, cmd_db)
    embedModel: EmbedModel = EmbedModel(cmd)
    embedModel.set_title(embedData[0])
    embedModel.set_description(embedData[1])
    embedModel.set_footer(embedData[2])
    embedModel.set_thumbnail(embedData[3])
    embedModel.set_image(embedData[4])
    embedModel.set_fields(embedData[5])

    if cmd == "meme":
        embedModel.set_image(meme.get_random_meme())

    return embedModel


def parse_embed_msg(embed: EmbedModel, msg: str):
    sections: List = msg.split("\n")
    for s in sections[1:]:
        section_name: str = s.split("=", 1)[0]
        section_text: str = s.split("=", 1)[1]

        if section_name == "TITLE":
            embed.set_title(section_text)
        elif section_name == "DESCRIPTION":
            embed.set_description(section_text)
        elif section_name == "FOOTER":
            embed.set_footer(section_text)
        elif section_name == "THUMBNAIL" and url.is_image(section_text):
            embed.set_thumbnail(section_text)
        elif section_name == "IMAGE" and url.is_image(section_text):
            embed.set_image(section_text)
        else:
            embed.add_field(section_name, section_text)

    return embed
