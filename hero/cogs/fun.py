from random import randint, seed, choice
from datetime import datetime, time
from os import path

from discord import Embed
from discord.ext import commands, tasks

from hero.utils import embeds, url
from hero.utils.embed_model import EmbedModel

# TODO: this is literally a text file, will need a table for this some day
meme_path: str = "databases/memes"
heads: str = "https://i.imgur.com/dTNbMle.png"
tails: str = "https://i.imgur.com/Suza17V.png"
meme_msg: str = "I {} this meme."
dbz_gif: str = "https://media.tenor.com/images/f1d0693271bdf3259481a1e54d184673/tenor.gif"
hero_time_vid: str = "https://cdn.discordapp.com/attachments/509819835874541570/761054332652879932/video0.mp4"


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.hero_time.start()

    # Adds the meme from the given link and sends it back
    @commands.command(name="addmeme")
    @commands.has_permissions(ban_members=True)
    async def add_meme(self, ctx: commands.Context, meme_link: str):
        if url.is_image(meme_link):
            with open(meme_path, "a") as f:
                f.write("\n" + meme_link)
            await self.send_meme(ctx, meme_link)
            await ctx.send(meme_msg.format("added"))
        else:
            await ctx.send("That is not a valid image url.")

    @commands.command(name="removememe")
    @commands.has_permissions(ban_members=True)
    async def remove_meme(self, ctx: commands.Context, meme_link: str):
        if url.is_image(meme_link):
            found = False
            with open(meme_path, "r") as f:
                memes = f.readlines()
            with open(meme_path, "w") as f:
                for meme in memes:
                    if meme.strip("\n") != meme_link and len(meme) > 0:
                        f.write(meme)
                    else:
                        found = True
                        await self.send_meme(ctx, meme_link)
                        await ctx.send(meme_msg.format("removed"))
            if not found:
                await ctx.send("I did not find that meme. You need the exact link.")
        else:
            await ctx.send("That is not a valid image url.")

    # Sends a random meme from the memes file
    @commands.command(name="meme")
    async def meme(self, ctx: commands.Context):
        if not path.exists(meme_path):
            open(meme_path, "w+")
        with open(meme_path, "r") as f:
            seed()
            try:
                meme: str = choice(f.readlines())
            except:
                await ctx.send("There are no memes")
                return
        await self.send_meme(ctx, meme)

    # Flips a coin
    @commands.command(name="coin")
    async def coin(self, ctx: commands.Context):
        model: EmbedModel = EmbedModel("coin")
        model.set_title("HEADS")
        model.set_image(heads)

        if randint(1, 100) % 2 != 0:
            model.set_title("TAILS")
            model.set_image(tails)

        embed: Embed = embeds.create_embed(model)
        await ctx.send(embed=embed)

    # Rolls a dice with a given number of sides. Some funny messages for funny numbers
    @commands.command(name="roll")
    async def roll(self, ctx: commands.Context, dice_sides: int):
        if dice_sides in [69, 420]:
            await ctx.send("Not funny. Didn't laugh 😐")
        else:
            dice_sides = dice_sides if dice_sides < 1000000000 else 1000000000
            roll: int = randint(1, dice_sides)
            if roll == 9001:
                model: EmbedModel = EmbedModel("9001")
                model.set_image(dbz_gif)
                embed: Embed = embeds.create_embed(model)
                await ctx.send(embed=embed)
            await ctx.send("🎲 {} rolled **{}** 🎲".format(ctx.author.mention, roll))

    @add_meme.error
    async def perm_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("{} you do not have permission to do that!".format(ctx.author.mention))
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(error)

    @roll.error
    async def roll_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(error)
        else:
            await ctx.send("That is not a number.")

    @tasks.loop(seconds=1)
    async def hero_time(self):
        now = datetime.now()
        if now.hour == 5 and now.minute == 38 and now.second == 0:
            chan = self.bot.get_channel(509819835874541570)
            await chan.send("**IT'S HERO TIME\n**{}".format(hero_time_vid))

    @hero_time.before_loop
    async def before_hero_time(self):
        await self.bot.wait_until_ready()

    async def send_meme(self, ctx: commands.Context, meme_link: str):
        embed_model: EmbedModel = EmbedModel("meme")
        embed_model.set_image(meme_link)
        embed: Embed = embeds.create_embed(embed_model)
        await ctx.send(embed=embed)
