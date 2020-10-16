from typing import List
from sqlite3 import Connection

from discord import Game, Embed, Message, Intents
from discord.ext import commands

from secret import token
from hero import embeds, boost, cmd_database, info, fun, medals, custom, mods
from hero.embed_model import EmbedModel

prefix: str = "?"
status_msg: str = "Type ?info"
intents = Intents.default()
intents.members = True
bot: commands.Bot = commands.Bot(
    command_prefix=prefix,
    help_command=None,
    activity=Game(status_msg),
    intents=intents)


@bot.event
async def on_message(msg: Message):
    if bot.user == msg.author or len(msg.content) == 0 or msg.content[0] != prefix:
        return

    cmd: str = msg.content.split()[0][1:]
    cmd_db: Connection = cmd_database.connect_to_cmd_db()
    text_cmds: List = cmd_database.select_all_text_cmds(cmd_db)
    embed_cmds: List = cmd_database.select_all_embed_cmds(cmd_db)

    if cmd in text_cmds:
        text: str = cmd_database.select_text_cmd(cmd, cmd_db)
        await msg.channel.send(text)
        return
    elif cmd in embed_cmds:
        embed_model: EmbedModel = embeds.get_embed_model(cmd)
        embed: Embed = embeds.create_embed(embed_model)
        await msg.channel.send(embed=embed)
        return

    await bot.process_commands(msg)


@bot.command(name="info")
async def cmd_info(ctx: commands.Context, *args):
    await info.send_info(bot, ctx, args)


@bot.command(name="boostboard")
async def boostboard(ctx: commands.Context):
    await boost.send_boostboard(ctx)


@bot.command(name="boost")
async def boost_msg(ctx: commands.Context):
    await boost.send_boost_msg(ctx)


@bot.command(name="coin")
async def coin(ctx: commands.Context):
    await fun.flip_coin(ctx)


@bot.command(name="givemedal", aliases=["addmedal"])
@commands.has_permissions(administrator=True)
async def give_medal(ctx: commands.Context, *args):
    await medals.give_medal(ctx, args)


@bot.command(name="removemedal")
@commands.has_permissions(administrator=True)
async def remove_medal(ctx: commands.Context, *args):
    await medals.remove_medal(ctx, args)


@bot.command(name="medalboard", aliases=["medalslist", "medallist", "medalsboard"])
async def medalboard(ctx: commands.Context, *args):
    await medals.send_medalboard(bot, ctx, args)


@bot.command(name="medals", aliases=["minimedals", "medal"])
async def get_medals(ctx: commands.Context, *args):
    await medals.send_medals(ctx, args)


@bot.command(name="addcommand", aliases=["addcmd"])
@commands.has_permissions(administrator=True)
async def add_cmd(ctx: commands.Context, *args):
    await custom.add_cmd(ctx, args)


@bot.command(name="removecommand", aliases=["removecmd"])
@commands.has_permissions(administrator=True)
async def remove_cmd(ctx: commands.Context, *args):
    await custom.rm_cmd(ctx, args)


@bot.command(name="addmeme")
@commands.has_permissions(ban_members=True)
async def add_meme(ctx: commands.Context, *args):
    await fun.add_meme(ctx, args)


@bot.command(name="slowmode", aliases=["funmode"])
@commands.has_permissions(manage_channels=True)
async def slow_mode(ctx: commands.Context, seconds: int):
    await mods.slow_mode(ctx, seconds)


# @bot.command(name="kick")
# @commands.has_permissions(kick_members=True)
# async def kick(ctx: commands.Context, *args):
#     await mods.kick(ctx, args)

@add_cmd.error
@remove_cmd.error
@add_meme.error
@give_medal.error
@remove_medal.error
@slow_mode.error
async def perm_error(ctx: commands.Context, error: commands.CommandError):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("{} you do not have permission to do that!".format(ctx.author.mention))


# @kick.error
# async def ban_error(ctx: commands.Context, error: commands.CommandError):
#     if isinstance(error, commands.MissingPermissions):
#         await ctx.send("{} you do not have permission to do that!".format(ctx.author.mention))
#     else:
#         await ctx.send("Not even I have the power to do that")


bot.run(token)
