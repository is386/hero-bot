from typing import List
from sqlite3 import Connection

from discord import Game, Embed, Message
from discord.ext import commands

from secret import token
from hero import embeds, boost, cmd_database, info, meme, url, errors
from hero.embed_model import EmbedModel

prefix: str = "?"
status_msg: str = "Type ?info"
owners: List = [139148414507155457, 177830256294494209]

dab_emote: str = "<:HeroDab:619944332140478464>"

boost_msg: str = "What's up booster. Imagine not being a booster"
top10_msg: str = "**Top 10 Herocord Boosters**```{}```"
cmd_msg: str = "I {} the **?{}** command"
add_meme_msg: str = "I added this new meme"


bot: commands.Bot = commands.Bot(
    command_prefix=prefix,
    help_command=None,
    activity=Game(status_msg))


def is_owner():
    async def predicate(ctx):
        return ctx.author.id in owners
    return commands.check(predicate)


@bot.command(name="info")
async def send_help(ctx: commands.Context, *args):
    cmd_db: Connection = cmd_database.connect_to_cmd_db()
    if len(args) == 0:
        embed_model: EmbedModel = info.get_full_info()
        embed_model.set_thumbnail(bot.user.avatar_url)
    elif args[0] in cmd_database.select_all_custom_cmds(cmd_db):
        await ctx.send(errors.no_custom_info)
        return
    elif args[0] in cmd_database.select_all_cmds(cmd_db):
        embed_model: EmbedModel = info.get_cmd_info(args[0])
    else:
        await ctx.send(errors.invalid_cmd)
        return

    embed: Embed = embeds.create_embed(embed_model)
    await ctx.send(embed=embed)


@bot.command(name="boosters")
async def send_leaderboard(ctx: commands.Context):
    boosters: dict = boost.get_boosters(ctx)
    if len(boosters) == 0:
        await ctx.send(errors.no_boosts)
        return

    msg: str = boost.build_leaderboard(boosters)
    await ctx.send(top10_msg.format(msg))


@bot.command(name="boost")
async def send_funny_boost(ctx: commands.Context):
    if ctx.author in ctx.guild.premium_subscribers:
        await ctx.send(boost_msg)
    else:
        await ctx.message.add_reaction(dab_emote)


@bot.command(name="addcommand", aliases=["addcmd"])
@is_owner()
async def add_cmd(ctx: commands.Context, *args):
    cmd_db: Connection = cmd_database.connect_to_cmd_db()
    if len(args) < 2:
        await ctx.send(errors.add_cmd_fmt)
        return

    if args[0] == "embed":
        name: str = args[1]
        embed_model: EmbedModel = EmbedModel(name)
        embed_model = embeds.parse_embed_msg(embed_model, ctx.message.content)
        if name not in cmd_database.select_all_cmds(cmd_db):
            cmd_database.insert_embed_cmd(embed_model, cmd_db)
            await ctx.send(cmd_msg.format("created", name))
        elif name in cmd_database.select_all_custom_cmds(cmd_db):
            cmd_database.update_embed_cmd(embed_model, cmd_db)
            await ctx.send(cmd_msg.format("updated", name))
        else:
            await ctx.send(errors.no_update_cmd)
            return

        embed: Embed = embeds.create_embed(embed_model)
        await ctx.send(embed=embed)
    else:
        name: str = args[0]
        text: str = " ".join(args[1:])
        if name in cmd_database.select_all_embed_cmds(cmd_db):
            await ctx.send(errors.wrong_cmd_type)
            return
        if name not in cmd_database.select_all_cmds(cmd_db):
            cmd_database.insert_text_cmd(name, text, cmd_db)
            await ctx.send(cmd_msg.format("created", name))
        elif name in cmd_database.select_all_custom_cmds(cmd_db):
            cmd_database.update_text_cmd(name, text, cmd_db)
            await ctx.send(cmd_msg.format("updated", name))
        else:
            await ctx.send(errors.no_update_cmd)
            return

        text: str = cmd_database.select_text_cmd(name, cmd_db)
        await ctx.send(text)


@bot.command(name="removecommand", aliases=["removecmd"])
@is_owner()
async def remove_cmd(ctx: commands.Context, *args):
    cmd_db: Connection = cmd_database.connect_to_cmd_db()
    if len(args) == 0:
        await ctx.send(errors.rm_cmd_fmt)
    else:
        cmd: str = args[0]
        if cmd in cmd_database.select_all_custom_cmds(cmd_db):
            if cmd in cmd_database.select_all_text_cmds(cmd_db):
                cmd_database.remove_text_cmd(cmd, cmd_db)
            else:
                cmd_database.remove_embed_cmd(cmd, cmd_db)
            await ctx.send(cmd_msg.format("removed", cmd))
        else:
            await ctx.send(errors.no_rm_cmd)


@bot.command(name="addmeme")
@is_owner()
async def add_meme(ctx: commands.Context, *args):
    if len(args) == 0:
        await ctx.send(errors.no_meme_given)
    elif url.is_image(args[0]):
        meme.add_meme(args[0])
        embed_model: EmbedModel = EmbedModel("NewMeme")
        embed_model.set_image(args[0])
        embed: Embed = embeds.create_embed(embed_model)
        await ctx.send(embed=embed)
        await ctx.send(add_meme_msg)
    else:
        await ctx.send(errors.not_img_url)


@add_cmd.error
@remove_cmd.error
@add_meme.error
async def cmd_error(ctx: commands.Context, error: commands.CommandError):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(errors.not_admin.format(ctx.author.mention))
    else:
        await ctx.send(errors.not_owner.format(ctx.author.mention))


@bot.event
async def on_message(msg: Message):
    if bot.user == msg.author or msg.content[0] != prefix:
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

bot.run(token)
