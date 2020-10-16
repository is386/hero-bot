from typing import List
from sqlite3 import Connection
from discord.ext import commands
from hero import medal_database, errors

medals_msg: str = "{} has {} minimedals <:MiniMedal:588443225358991412>"
medal_board_msg: str = "**Top 10 Herocord Minimedalists**```{}```"


async def give_medal(ctx: commands.Context, args: List):
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


async def remove_medal(ctx: commands.Context, args: List):
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


async def send_medalboard(bot: commands.Bot, ctx: commands.Context, args: List):
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
        s += "{:}. {: <32} {}\n".format(c, k, new_dict[k])
        c += 1

    await ctx.send(medal_board_msg.format(s))


async def send_medals(ctx: commands.Context, args: List):
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
