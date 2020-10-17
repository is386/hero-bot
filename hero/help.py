from sqlite3 import Connection
from typing import List

from discord import Embed
from discord.ext import commands

from hero.embed_model import EmbedModel
from hero import cmd_database, embeds


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="info")
    async def help(self, ctx: commands.Context, *args):
        cmd_db: Connection = cmd_database.connect_to_cmd_db()
        if len(args) == 0:
            embed_model: EmbedModel = self.get_all_cmds()
            embed_model.set_thumbnail(self.bot.user.avatar_url)
        elif args[0] in cmd_database.select_all_custom_cmds(cmd_db):
            await ctx.send("I cannot help with custom commands.")
            return
        elif args[0] in cmd_database.select_all_cmds(cmd_db):
            embed_model: EmbedModel = self.get_cmd_help(args[0])
        else:
            await ctx.send("That command does not exist.")
            return

        embed: Embed = embeds.create_embed(embed_model)
        await ctx.send(embed=embed)

    def get_all_cmds(self):
        embedModel: EmbedModel = EmbedModel("help")
        embedModel.set_title("Commands List")
        embedModel.set_description("`?info <command>` for more help.")
        embedModel.set_footer("By: 1nder")
        cmd_db: Connection = cmd_database.connect_to_cmd_db()
        categories: List = sorted(
            cmd_database.select_all_categories(cmd_db))

        for cat in categories:
            cmds: List = cmd_database.select_cmds_in_category(cat, cmd_db)
            for i, c in enumerate(cmds):
                cmds[i] = "`{}`".format(c)
            embedModel.add_field(cat, ", ".join(cmds))

        return embedModel

    def get_cmd_help(self, cmd: str):
        embedModel: EmbedModel = EmbedModel("help")
        cmd_db: Connection = cmd_database.connect_to_cmd_db()
        cmdHelp: tuple = cmd_database.select_cmd_info(cmd, cmd_db)
        embedModel.set_title("Command Usage: ?{}".format(cmd))
        embedModel.set_description(cmdHelp[0])
        embedModel.add_field("Usage", "`{}`".format(cmdHelp[1]))

        if cmdHelp[2] is not None:
            examples: List = cmdHelp[2].split(",")
            for i, e in enumerate(examples):
                examples[i] = "`{}`".format(e)
            embedModel.add_field("Example", "\n".join(examples))

        return embedModel
