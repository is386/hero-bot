from sqlite3 import Connection
from discord.ext import commands
from hero.utils import medal_database

medals_msg: str = "{} has {} minimedals <:MiniMedal:588443225358991412>"
medal_earned: str = "What luck! {} finds a mini medal <:MiniMedal:588443225358991412>"
medal_lost: str = "What despair! {} lost a mini medal <:MiniMedal:588443225358991412>"
medal_board_msg: str = "**Top 10 Herocord Minimedalists**```{}```"


class Medals(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Increments the medal count for a user
    @commands.command(name="givemedal", aliases=["addmedal"])
    @commands.has_permissions(administrator=True)
    async def give_medal(self, ctx: commands.Context, user_ping: str):
        user: int = self.parse_mention(user_ping)
        if not user:
            await ctx.send("That is a bad user id. Please ping the user with the command.")

        medal_db: Connection = medal_database.connect_to_db()
        c: int = 1

        # Inserts or updates depending on if the user exists in the db
        if medal_database.user_exists(medal_db, user):
            c = medal_database.select_count(medal_db, user) + 1
            medal_database.update_count(medal_db, user, c)
        else:
            medal_database.insert_count(medal_db, user)

        await ctx.send(medal_earned.format(user_ping, c))

    # Reduces the medal count for a user
    @commands.command(name="removemedal")
    @commands.has_permissions(administrator=True)
    async def remove_medal(self, ctx: commands.Context, user_ping: str):
        user: int = self.parse_mention(user_ping)
        if not user:
            await ctx.send("That is a bad user id. Please ping the user with the command.")

        medal_db: Connection = medal_database.connect_to_db()
        c: int = medal_database.select_count(medal_db, user)

        # If the count is greater than 0
        if c:
            c -= 1
            medal_database.update_count(medal_db, user, c)

        await ctx.send(medal_lost.format(user_ping))

    # Sends a leaderboard with users who have the most medals
    @commands.command(name="medalboard", aliases=["medalslist", "medallist", "medalsboard"])
    async def medalboard(self, ctx: commands.Context):
        medal_db: Connection = medal_database.connect_to_db()

        # Gets the top ten users with the most medals from the db
        medal_dict: dict = medal_database.select_ten(medal_db)
        new_dict: dict = {}

        # Removes anyone in the top 10 with 0 medals
        for user_id in medal_dict.keys():
            if medal_dict[user_id] != 0:
                user = await self.bot.fetch_user(user_id)
                new_dict[user.name] = medal_dict[user_id]

        if len(new_dict) == 0:
            await ctx.send("No clout to be had here")
            return

        c: int = 1
        s: str = ""

        # Builds a string that looks like a leaderboard
        for k in new_dict.keys():
            s += "{:}. {: <32} {}\n".format(c, k, new_dict[k])
            c += 1

        await ctx.send(medal_board_msg.format(s))

    # Sends the number of medals a user has
    @commands.command(name="medals", aliases=["minimedals", "medal"])
    async def get_medals(self, ctx: commands.Context, *args):
        if len(args) < 1:
            user: int = ctx.author.id
            mention: str = ctx.author.mention
        else:
            user: int = self.parse_mention(args[0])
            if not user:
                await ctx.send("That is a bad user id. Please ping the user with the command.")
            mention: str = args[0]

        medal_db: Connection = medal_database.connect_to_db()
        c: int = medal_database.select_count(medal_db, user)
        await ctx.send(medals_msg.format(mention, c))

    @give_medal.error
    @remove_medal.error
    async def perm_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("{} you do not have permission to do that!".format(ctx.author.mention))
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(error)

    # Returns the userid from a mention string
    def parse_mention(self, mention: str) -> int:
        try:
            return int(''.join(i for i in mention if i.isalnum()))
        except ValueError:
            return None
