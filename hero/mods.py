from discord import Message, Embed, Member
from discord.ext import commands
from hero import errors, embeds, reactions
from hero.embed_model import EmbedModel


async def slow_mode(ctx: commands.Context, seconds: int):
    if seconds < 0:
        seconds = 0
    elif seconds > 21600:
        seconds = 21600
    await ctx.channel.edit(slowmode_delay=seconds)
    await ctx.send("{} second funmode has been activated".format(seconds))


async def kick(ctx: commands.Context, args):
    if len(args) < 2:
        await ctx.send(errors.bad_kick)
        return

    try:
        user_id: int = int(''.join(i for i in args[0] if i.isalnum()))
    except ValueError:
        await ctx.send(errors.bad_name)
        return

    reason: str = " ".join(args[1:])
    user: Member = ctx.guild.get_member(user_id)
    if not user:
        await ctx.send(errors.no_user)

    model: EmbedModel = EmbedModel("kick")
    model.set_title("Kick {}".format(user))
    model.set_description(
        "Press the red button to kick. If 20 seconds pass, the user will not be kicked.")
    model.set_fields({"Reason": reason})
    embed: Embed = embeds.create_embed(model)
    resp: Message = await ctx.send(embed=embed)

    confirm_kick: bool = await reactions.confirm(ctx, resp)
    if confirm_kick:
        await user.kick(reason=reason)
        await ctx.send("**{}** was kicked for **{}**".format(user.name, reason))
    else:
        await ctx.send("The kick was cancelled.")
