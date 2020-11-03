from sqlite3 import Connection
from typing import List

from discord import Guild, Member
from discord.ext import commands
from hero.utils import server_database


class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Allows for the setting of the welcome message
    @commands.command(name="welcome")
    @commands.has_permissions(administrator=True)
    async def welcome(self, ctx: commands.Context, *args):
        if len(args) < 1:
            await ctx.send("That's not right. The format is `?welcome <message>.`")
            return

        server_db: Connection = server_database.connect_to_db()
        msg: str = " ".join(args)
        server: int = ctx.guild.id
        chan: int = ctx.channel.id
        # If the server does not already have a welcome message set
        if not server_database.select_welcome(server_db, ctx.guild.id):
            server_database.insert_welcome(server_db, server, chan, msg)
        else:
            server_database.update_welcome(server_db, server, chan, msg)

        await ctx.send("This is now the welcome channel. The message is `@User {}`.".format(msg))

    # Sends a welcome message when a user joins the server
    # TODO: Send no message if the server did not set up a welcome message
    @commands.Cog.listener()
    async def on_member_join(self, member: Member):
        guild: Guild = member.guild
        server_db: Connection = server_database.connect_to_db()
        welcome: List = server_database.select_welcome(server_db, guild.id)
        chan = guild.get_channel(welcome[0])
        await chan.send("{} {}".format(member.mention, welcome[1]))

    @welcome.error
    async def perm_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("{} you do not have permission to do that!".format(ctx.author.mention))
