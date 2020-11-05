from discord import Embed, Member, Message, utils
from discord import mentions
from discord.ext import commands
from hero.utils import embeds, reactions
from hero.utils.embed_model import EmbedModel

bad_user: str = "That user does not exist. Did you try pinging the user?"


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

    # Kicks a user from the server
    @commands.command(name="kick")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx: commands.Context, *args):
        if len(args) < 2:
            await ctx.send("That's not right. The format is `?kick <ping> <reason>`.")
            return

        user: Member = self.parse_mention(ctx, args[0])
        if not user:
            await ctx.send(bad_user)
            return

        reason: str = " ".join(args[1:])
        embed: Embed = self.get_infraction_embed(user, reason, "kick")
        resp: Message = await ctx.send(embed=embed)
        # Waits for a mod to confirm their choice before kicking
        confirm_kick: bool = await reactions.confirm(ctx, resp)

        if confirm_kick:
            await user.kick(reason=reason)
            await ctx.send("**{}** was kicked for **{}**.".format(user.name, reason))
        else:
            await ctx.send("The kick was cancelled.")

    # Bans a user from the server
    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx: commands.Context, *args):
        if len(args) < 2:
            await ctx.send("That's not right. The format is `?ban <ping> <reason>`.")
            return

        user: Member = self.parse_mention(ctx, args[0])
        if not user:
            await ctx.send(bad_user)
            return

        reason: str = " ".join(args[1:])
        embed: Embed = self.get_infraction_embed(user, reason, "ban")
        resp: Message = await ctx.send(embed=embed)
        # Waits for a mod to confirm their choice before banning
        confirm_ban: bool = await reactions.confirm(ctx, resp)

        if confirm_ban:
            await user.ban(reason=reason)
            await ctx.send("**{}** was banned for **{}**.".format(user.name, reason))
        else:
            await ctx.send("The ban was cancelled.")

    @commands.command(name="mute")
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, *args):
        if len(args) < 2:
            await ctx.send("That's not right. The format is `?mute <ping> <reason>`.")
            return

        user: Member = self.parse_mention(ctx, args[0])
        if not user:
            await ctx.send(bad_user)
            return

        reason: str = " ".join(args[1:])
        embed: Embed = self.get_infraction_embed(user, reason, "mute")
        resp: Message = await ctx.send(embed=embed)
        # Waits for a mod to confirm their choice before muting
        confirm_mute: bool = await reactions.confirm(ctx, resp)

        if confirm_mute:
            role = utils.get(user.guild.roles, name="Snoozed")
            if not role:
                role = await user.guild.create_role(name="Snoozed")
            await user.add_roles(role)
            await ctx.send("**{}** was muted for **{}**.".format(user.name, reason))
        else:
            await ctx.send("The mute was cancelled.")

    @kick.error
    @ban.error
    @mute.error
    async def ban_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("{} you do not have permission to do that!".format(ctx.author.mention))
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
