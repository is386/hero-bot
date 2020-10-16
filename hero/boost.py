from typing import List
from datetime import datetime, timedelta

from discord import Member
from discord.ext import commands


def get_boosters(ctx: commands.Context):
    today: datetime = datetime.today()
    boosters: List[Member] = ctx.guild.premium_subscribers
    ranks: dict = {}

    for b in boosters:
        ranks[str(b)] = (today - b.premium_since).total_seconds()

    ranks = {k: v for k, v in sorted(ranks.items(), key=lambda item: item[1])}
    for r in list(ranks.keys())[:len(ranks.keys()) - 11:-1]:
        ranks[r] = timedelta(seconds=ranks[r])

    return ranks


def build_leaderboard(boosters: dict):
    c: int = 1
    s: str = ""

    for b in list(boosters.keys())[:len(boosters.keys()) - 11:-1]:
        s += "{:}. {: <32} {}\n".format(c, b[0:len(b) - 5], boosters[b])
        c += 1

    return s
