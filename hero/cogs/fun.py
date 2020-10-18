from random import randint, seed, choice
from discord import Embed
from discord.ext import commands
from hero.utils import embeds, url
from hero.utils.embed_model import EmbedModel

meme_path: str = "databases/memes"
heads: str = "https://i.imgur.com/dTNbMle.png"
tails: str = "https://i.imgur.com/Suza17V.png"
add_meme_msg: str = "I added this new meme"
dbz_gif: str = "https://media.tenor.com/images/f1d0693271bdf3259481a1e54d184673/tenor.gif"


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="addmeme")
    @commands.has_permissions(ban_members=True)
    async def add_meme(self, ctx: commands.Context, meme_link: str):
        if url.is_image(meme_link):
            with open(meme_path, "a") as f:
                f.write("\n" + meme_link)
            embed_model: EmbedModel = EmbedModel("NewMeme")
            embed_model.set_image(meme_link)
            embed: Embed = embeds.create_embed(embed_model)
            await ctx.send(embed=embed)
            await ctx.send(add_meme_msg)
        else:
            await ctx.send("That is not a valid image url.")

    @commands.command(name="meme")
    async def send_meme(self, ctx: commands.Context):
        with open(meme_path, "r") as f:
            seed()
            meme: str = choice(f.readlines())
        model: EmbedModel = EmbedModel("meme")
        model.set_image(meme)
        embed: Embed = embeds.create_embed(model)
        await ctx.send(embed=embed)

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
            else:
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
