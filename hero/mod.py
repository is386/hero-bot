from discord import Embed, Member, Message
from discord.ext import commands
from hero import embeds, reactions
from hero.embed_model import EmbedModel

bad_user: str = "That user does not exist. Did you try pinging the user?"


class Mod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="slowmode", aliases=["funmode"])
    @commands.has_permissions(manage_channels=True)
    async def slow_mode(self, ctx: commands.Context, seconds: int):
        if seconds < 0:
            seconds = 0
        elif seconds > 21600:
            seconds = 21600
        await ctx.channel.edit(slowmode_delay=seconds)
        await ctx.send("{} second funmode has been activated.".format(seconds))

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
        confirm_kick: bool = await reactions.confirm(ctx, resp)

        if confirm_kick:
            await user.kick(reason=reason)
            await ctx.send("**{}** was kicked for **{}**.".format(user.name, reason))
        else:
            await ctx.send("The kick was cancelled.")

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
        confirm_ban: bool = await reactions.confirm(ctx, resp)

        if confirm_ban:
            await user.ban(reason=reason)
            await ctx.send("**{}** was banned for **{}**.".format(user.name, reason))
        else:
            await ctx.send("The ban was cancelled.")

    @slow_mode.error
    async def perm_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("{} you do not have permission to do that!".format(ctx.author.mention))

    @kick.error
    @ban.error
    async def ban_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("{} you do not have permission to do that!".format(ctx.author.mention))
        else:
            await ctx.send("They are too powerful...")

    def parse_mention(self, ctx: commands.Context, mention: str):
        try:
            user: int = int(''.join(i for i in mention if i.isalnum()))
            return ctx.guild.get_member(user)
        except ValueError:
            return None

    def get_infraction_embed(self, user: Member, reason: str, inf_type: "str"):
        model: EmbedModel = EmbedModel(inf_type)
        model.set_title(
            "Are you sure you want to {} {}?".format(inf_type, user))
        model.set_description(
            "Press the red button within 20 seconds to {}.".format(inf_type))
        model.set_fields({"Reason": reason})
        return embeds.create_embed(model)
