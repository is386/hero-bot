from typing import List
from sqlite3 import Connection

from discord import Embed, Member, Message, utils, Role,  VoiceChannel, TextChannel, PermissionOverwrite, User
from discord.abc import GuildChannel
from discord.ext import commands

from hero.utils import embeds, reactions, history_database
from hero.utils.embed_model import EmbedModel

bad_user: str = "That user does not exist. Did you try pinging the user?"
mute_role: str = "Snooze"

text_mute_perms: PermissionOverwrite = PermissionOverwrite()
text_mute_perms.send_messages = False
text_mute_perms.send_tts_messages = False
text_mute_perms.attach_files = False
text_mute_perms.add_reactions = False

voice_mute_perms: PermissionOverwrite = PermissionOverwrite()
voice_mute_perms.connect = False


class Mod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Sets the chat to slowmode
    @commands.command(name="slowmode", aliases=["funmode"])
    @commands.has_permissions(manage_channels=True)
    async def slow_mode(self, ctx: commands.Context, seconds: int):
        if seconds < 0:
            seconds = 0
        elif seconds > 21600:  # 6 hour limit
            seconds = 21600
        await ctx.channel.edit(slowmode_delay=seconds)
        await ctx.send("{} second funmode has been activated.".format(seconds))

    # Sends the users infraction history
    @commands.command(name="history", aliases=["lore"])
    @commands.has_permissions(kick_members=True)
    async def history(self, ctx, mention: str):
        user: Member = self.parse_mention(ctx, mention)
        if not user:
            await ctx.send(bad_user)
            return
        db: Connection = history_database.connect_to_db()
        infractions: List = history_database.select_history(db, user.id)
        if infractions:
            embed: Embed = self.get_history_embed(user, infractions)
            await ctx.send(embed=embed)
        else:
            await ctx.send("**{}** has no infraction history.".format(user.name))

    # Kicks a user from the server
    @commands.command(name="kick")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx: commands.Context, *args):
        user, reason, confirm = await self.prep_infraction(ctx, args, "kick")
        if confirm:
            await user.kick(reason=reason)
            await ctx.send("**{}** was kicked for **{}**.".format(user.name, reason))
            db: Connection = history_database.connect_to_db()
            history_database.insert_infraction(
                db, user.id, ctx.author.id, "kick", reason)
        elif user and not confirm:
            await ctx.send("The kick was cancelled.")

    # Bans a user from the server
    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx: commands.Context, *args):
        user, reason, confirm = await self.prep_infraction(ctx, args, "ban")
        if confirm:
            await user.ban(reason=reason)
            await ctx.send("**{}** was banned for **{}**.".format(user.name, reason))
            db: Connection = history_database.connect_to_db()
            history_database.insert_infraction(
                db, user.id, ctx.author.id, "ban", reason)
        elif user and not confirm:
            await ctx.send("The ban was cancelled.")

    # Bans a user from the server
    @commands.command(name="warn")
    @commands.has_permissions(kick_members=True)
    async def warn(self, ctx: commands.Context, *args):
        user, reason, confirm = await self.prep_infraction(ctx, args, "warn")
        if confirm:
            await ctx.send("**{}** was warned for **{}**.".format(user.name, reason))
            db: Connection = history_database.connect_to_db()
            history_database.insert_infraction(
                db, user.id, ctx.author.id, "warn", reason)
        elif user and not confirm:
            await ctx.send("The warn was cancelled.")

    # Mutes the given user
    @commands.command(name="mute", aliases=["snooze"])
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, *args):
        user, reason, confirm = await self.prep_infraction(ctx, args, "mute")
        if confirm:
            if utils.get(user.roles, name=mute_role):
                await ctx.send("This user is already afflicted by snooze.")
                return
            role: Role = utils.get(user.guild.roles, name=mute_role)
            # Creates the role if it doesn't exist
            if not role:
                role = await user.guild.create_role(name=mute_role)
            await user.add_roles(role)
            await ctx.send("**{}** was snoozed for **{}**.".format(user.name, reason))
            db: Connection = history_database.connect_to_db()
            history_database.insert_infraction(
                db, user.id, ctx.author.id, "mute", reason)
        elif user and not confirm:
            await ctx.send("Snooze missed.")

    # Unmutes the given user
    @commands.command(name="unmute", aliases=["unsnooze"])
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, mention: str):
        user: Member = self.parse_mention(ctx, mention)
        if not user:
            await ctx.send(bad_user)
            return
        role: Role = utils.get(user.roles, name=mute_role)
        if role:
            await user.remove_roles(role)
            await ctx.send("**{}** was woken up from snooze.".format(user.name))
        else:
            await ctx.send("This user was never snoozed.")

    # Adds the mute role permissions to every channel
    @commands.command(name="addmute")
    @commands.has_permissions(manage_channels=True)
    async def addmute(self, ctx):
        for chan in ctx.guild.channels:
            await self.add_mute_role(chan)
        await ctx.send("I added the mute role to all channel permissions.")

    # Adds the muted role every time a new text or voice channel is created
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: GuildChannel):
        await self.add_mute_role(channel)

    # Prepares an infraction by checking command form, user id, and sending a confirm message.
    async def prep_infraction(self, ctx: commands.Context, args: List[str], cmd: str) -> bool:
        if len(args) < 2:
            await ctx.send("That's not right. The format is `?{} <ping> <reason>`.".format(cmd))
            return None, None, None

        user: Member = self.parse_mention(ctx, args[0])
        if not user:
            await ctx.send(bad_user)
            return None, None, None

        reason: str = " ".join(args[1:])
        embed: Embed = self.get_infraction_embed(user, reason, cmd)
        resp: Message = await ctx.send(embed=embed)
        # Waits for a mod to confirm their choice before banning
        return user, reason, await reactions.confirm(ctx, resp)

    # Parses the userid from a mention and returns a Member object
    def parse_mention(self, ctx: commands.Context, mention: str) -> Member:
        try:
            user: int = int(''.join(i for i in mention if i.isalnum()))
            return ctx.guild.get_member(user)
        except ValueError:
            return None

    # Creates the kick confirmation embed message
    def get_infraction_embed(self, user: Member, reason: str, inf_type: "str") -> Embed:
        model: EmbedModel = EmbedModel(inf_type)
        model.set_title(
            "Are you sure you want to {} {}?".format(inf_type, user))
        model.set_description(
            "Press the red button within 20 seconds to {}.".format(inf_type))
        model.set_fields({"Reason": reason})
        return embeds.create_embed(model)

    # Creates the embed message that displays infractions for a user
    def get_history_embed(self, user: Member, infractions: List) -> Embed:
        model: EmbedModel = EmbedModel("history")
        model.set_title("Infraction History for {}".format(user.name))
        model.set_description("**ID:** {}".format(user.id))
        model.set_thumbnail(user.avatar_url)
        for inf in infractions:
            mod: User = self.bot.get_user(inf[1])
            field: str = inf[2].upper()
            value: str = "Mod: {}\nReason: {}\nDate: {}".format(
                mod.name, inf[3], inf[4])
            model.add_field(field, value)
        return embeds.create_embed(model)

    # Adds the muted role to a channel:
    async def add_mute_role(self, channel: GuildChannel):
        role: Role = utils.get(channel.guild.roles, name=mute_role)
        if not role:
            role = await channel.guild.create_role(name=mute_role)
        if isinstance(channel, TextChannel):
            await channel.set_permissions(role, overwrite=text_mute_perms)
        elif isinstance(channel, VoiceChannel):
            await channel.set_permissions(role, overwrite=voice_mute_perms)

    @kick.error
    @ban.error
    @mute.error
    @unmute.error
    @history.error
    async def ban_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("{} you do not have permission to do that!".format(ctx.author.mention))
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(error)
        else:
            await ctx.send("They are too powerful...")

    @slow_mode.error
    async def slow_mode_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("{} you do not have permission to do that!".format(ctx.author.mention))
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(error)
        else:
            await ctx.send("That is not a number.")
