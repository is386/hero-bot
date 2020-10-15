from typing import List
from sqlite3 import Connection

from discord import Game, Embed, Message
from discord.ext import commands

from secret import token
from hero import embeds, boost, cmd_database, info, meme, url, errors, medal_database
from hero.embed_model import EmbedModel

prefix: str = "?"
status_msg: str = "Type ?info"
owners: List = [139148414507155457, 177830256294494209]

dab_emote: str = "<:HeroDab:619944332140478464>"

boost_msg: str = "What's up booster. Imagine not being a booster"
top10_msg: str = "**Top 10 Herocord Boosters**```{}```"
cmd_msg: str = "I {} the **?{}** command"
add_meme_msg: str = "I added this new meme"
medals_msg: str = "{} has {} minimedals <:MiniMedal:588443225358991412>"
medal_board_msg: str = "**Top 10 Herocord Minimedalists**```{}```"

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


@bot.command(name="boostboard")
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


@bot.command(name="givemedal", aliases=["addmedal"])
@is_owner()
async def give_medal(ctx: commands.Context, *args):
    if len(args) < 1:
        await ctx.send(errors.give_medal_name)
        return

    try:
        user: int = int(''.join(i for i in args[0] if i.isalnum()))
    except ValueError:
        await ctx.send(errors.bad_name)
        return

    medal_db: Connection = medal_database.connect_to_db()
    c: int = 1

    if medal_database.user_exists(medal_db, user):
        c = medal_database.select_count(medal_db, user) + 1
        medal_database.update_count(medal_db, user, c)
    else:
        medal_database.insert_count(medal_db, user)

    await ctx.send(medals_msg.format(args[0], c))


@bot.command(name="removemedal")
@is_owner()
async def remove_medal(ctx: commands.Context, *args):
    if len(args) < 1:
        await ctx.send(errors.rm_medal_name)
        return

    try:
        user: int = int(''.join(i for i in args[0] if i.isalnum()))
    except ValueError:
        await ctx.send(errors.bad_name)
        return

    medal_db: Connection = medal_database.connect_to_db()
    c: int = medal_database.select_count(medal_db, user)
    
    if c:
        c -= 1
        medal_database.update_count(medal_db, user, c)

    await ctx.send(medals_msg.format(args[0], c))


@bot.command(name="medalboard", aliases=["medalslist", "medallist", "medalsboard"])
async def get_medals_list(ctx: commands.Context, *args):
    medal_db: Connection = medal_database.connect_to_db()
    medal_dict: dict = medal_database.select_all(medal_db)
    new_dict: dict = {}

    for user_id in medal_dict.keys():
        if medal_dict[user_id] != 0:
            user = await bot.fetch_user(user_id)
            new_dict[user.name] = medal_dict[user_id]

    if len(new_dict) == 0:
        await ctx.send("No clout to be had here")
        return

    c: int = 1
    s: str = ""

    for k in new_dict.keys():
        s += "{:}. {: <20} {}\n".format(c, k, new_dict[k])
        c += 1

    await ctx.send(medal_board_msg.format(s))


@bot.command(name="medals", aliases=["minimedals", "medal"])
async def get_medals(ctx: commands.Context, *args):
    if len(args) < 1:
        user: int = ctx.author.id
        mention: str = ctx.author.mention
    else:
        try:
            user: int = int(''.join(i for i in args[0] if i.isalnum()))
            mention = args[0]
        except ValueError:
            await ctx.send(errors.bad_name)
            return

    medal_db: Connection = medal_database.connect_to_db()
    c: int = medal_database.select_count(medal_db, user)
    await ctx.send(medals_msg.format(mention, c))


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
