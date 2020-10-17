from random import randint, seed, choice
from discord import Embed
from discord.ext import commands
from hero import embeds, url
from hero.embed_model import EmbedModel

meme_path: str = "databases/memes"
heads: str = "https://i.imgur.com/dTNbMle.png"
tails: str = "https://i.imgur.com/Suza17V.png"
add_meme_msg: str = "I added this new meme"


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
        ctx.send(embed=embed)

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

    @add_meme.error
    async def perm_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("{} you do not have permission to do that!".format(ctx.author.mention))
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(error)
