from typing import List
from datetime import datetime, timedelta
from discord import Member
from discord.ext import commands

dab_emote: str = "<:HeroDab:619944332140478464>"
boost_msg: str = "What's up booster. Imagine not being a booster"
top10_msg: str = "**Top 10 Herocord Boosters**```{}```"


class Boost(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="boostboard")
    async def boostboard(self, ctx: commands.Context):
        boosters: dict = self.get_boosters(ctx)
        if len(boosters) == 0:
            await ctx.send("This server has no boosts.")
            return

        msg: str = self.build_leaderboard(boosters)
        await ctx.send(top10_msg.format(msg))

    @commands.command(name="boost")
    async def boost_msg(self, ctx: commands.Context):
        if ctx.author in ctx.guild.premium_subscribers:
            await ctx.send(boost_msg)
        else:
            await ctx.message.add_reaction(dab_emote)

    def get_boosters(self, ctx: commands.Context):
        today: datetime = datetime.today()
        boosters: List[Member] = ctx.guild.premium_subscribers
        ranks: dict = {}

        for b in boosters:
            ranks[str(b)] = (today - b.premium_since).total_seconds()

        ranks = {k: v for k, v in sorted(
            ranks.items(), key=lambda item: item[1])}
        for r in list(ranks.keys())[:len(ranks.keys()) - 11:-1]:
            ranks[r] = timedelta(seconds=ranks[r])

        return ranks

    def build_leaderboard(self, boosters: dict):
        c: int = 1
        s: str = ""

        for b in list(boosters.keys())[:len(boosters.keys()) - 11:-1]:
            s += "{:}. {: <32} {}\n".format(c, b[0:len(b) - 5], boosters[b])
            c += 1

        return s
