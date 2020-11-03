from sqlite3 import Connection
from typing import List

from discord import Embed
from discord.ext import commands

from hero.utils.embed_model import EmbedModel
from hero.utils import cmd_database, embeds


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Either sends a list of all commands or sends information for a given command
    @commands.command(name="info")
    async def help(self, ctx: commands.Context, *args):
        cmd_db: Connection = cmd_database.connect_to_cmd_db()
        # If no parameter, send a list of all commands
        if len(args) == 0:
            embed_model: EmbedModel = self.get_all_cmds()
            embed_model.set_thumbnail(self.bot.user.avatar_url)
        # If the command is a custom command, there is no info about it
        elif args[0] in cmd_database.select_all_custom_cmds(cmd_db):
            await ctx.send("I cannot help with custom commands.")
            return
        # If the command is a built in, there is info
        elif args[0] in cmd_database.select_all_cmds(cmd_db):
            embed_model: EmbedModel = self.get_cmd_help(args[0])
        else:
            await ctx.send("That command does not exist.")
            return

        embed: Embed = embeds.create_embed(embed_model)
        await ctx.send(embed=embed)

    # Returns an embed model, where the fields are the command categories ("admins", "fun", "custom", etc)
    # and the text under each field are the commands for that category
    def get_all_cmds(self) -> EmbedModel:
        embedModel: EmbedModel = EmbedModel("help")
        embedModel.set_title("Commands List")
        embedModel.set_description("`?info <command>` for more help.")
        embedModel.set_footer("By: 1nder")
        cmd_db: Connection = cmd_database.connect_to_cmd_db()

        # Gets every command category, sorted
        categories: List = sorted(
            cmd_database.select_all_categories(cmd_db))

        for cat in categories:
            # Gets the commands in the category
            cmds: List = cmd_database.select_cmds_in_category(cat, cmd_db)
            # Makes a nice string with all the commands
            for i, c in enumerate(cmds):
                cmds[i] = "`{}`".format(c)
            # Sets the field with field name category, and text commands
            embedModel.add_field(cat, ", ".join(cmds))

        return embedModel

    # Returns an embed model with information about a specific command
    def get_cmd_help(self, cmd: str) -> EmbedModel:
        embedModel: EmbedModel = EmbedModel("help")
        cmd_db: Connection = cmd_database.connect_to_cmd_db()

        # Gets a tuple with the info for a command
        cmdHelp: tuple = cmd_database.select_cmd_info(cmd, cmd_db)
        embedModel.set_title("Command Usage: ?{}".format(cmd))

        # cmdHelp[0] = what the cmd does
        embedModel.set_description(cmdHelp[0])

        # cmdHelp[2] = example of usage
        embedModel.add_field("Usage", "`{}`".format(cmdHelp[1]))

        # cmdHelp[2] = example of usage
        # Some commands may not have examples but if they do this will
        # format each example to look nice
        if cmdHelp[2] is not None:
            examples: List = cmdHelp[2].split(",")
            for i, e in enumerate(examples):
                examples[i] = "`{}`".format(e)
            embedModel.add_field("Example", "\n".join(examples))

        return embedModel
