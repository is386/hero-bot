from sqlite3 import Connection
from discord import Embed
from discord.ext import commands
from hero import cmd_database, embeds
from hero.embed_model import EmbedModel

cmd_msg: str = "I {} the **?{}** command."


async def add_cmd(ctx: commands.Context, args):
    if len(args) < 2:
        await ctx.send("That's not right. The format is `?addcmd <type> <name> <text>`.")
        return

    if args[0] == "embed":
        await add_embed(ctx, args[1])
    else:
        await add_text(ctx, args[0], " ".join(args[1:]))


async def add_embed(ctx: commands.Context, name: str):
    cmd_db: Connection = cmd_database.connect_to_cmd_db()
    embed_model: EmbedModel = EmbedModel(name)
    embed_model = embeds.parse_embed_msg(embed_model, ctx.message.content)

    if name not in cmd_database.select_all_cmds(cmd_db):
        cmd_database.insert_embed_cmd(embed_model, cmd_db)
        await ctx.send(cmd_msg.format("created", name))
    elif name in cmd_database.select_all_custom_cmds(cmd_db):
        cmd_database.update_embed_cmd(embed_model, cmd_db)
        await ctx.send(cmd_msg.format("updated", name))
    else:
        await ctx.send("You cannot update that command.")
        return

    embed: Embed = embeds.create_embed(embed_model)
    await ctx.send(embed=embed)


async def add_text(ctx: commands.Context, name: str, text: str):
    cmd_db: Connection = cmd_database.connect_to_cmd_db()
    if name in cmd_database.select_all_embed_cmds(cmd_db):
        await ctx.send("This command is already an image/embed command. Please remove it if you want it to be a text command.")
        return

    if name not in cmd_database.select_all_cmds(cmd_db):
        cmd_database.insert_text_cmd(name, text, cmd_db)
        await ctx.send(cmd_msg.format("created", name))
    elif name in cmd_database.select_all_custom_cmds(cmd_db):
        cmd_database.update_text_cmd(name, text, cmd_db)
        await ctx.send(cmd_msg.format("updated", name))
    else:
        await ctx.send("You cannot update that command.")
        return

    text: str = cmd_database.select_text_cmd(name, cmd_db)
    await ctx.send(text)


async def rm_cmd(ctx: commands.Context, args):
    cmd_db: Connection = cmd_database.connect_to_cmd_db()
    if len(args) == 0:
        await ctx.send("That's not right. You didn't give the command name.")
    else:
        cmd: str = args[0]
        if cmd in cmd_database.select_all_custom_cmds(cmd_db):
            if cmd in cmd_database.select_all_text_cmds(cmd_db):
                cmd_database.remove_text_cmd(cmd, cmd_db)
            else:
                cmd_database.remove_embed_cmd(cmd, cmd_db)
            await ctx.send(cmd_msg.format("removed", cmd))
        else:
            await ctx.send("You cannot remove that command.")
