from random import choice, seed, randint

from discord import Embed
from discord.ext import commands

from hero import embeds, url
from hero.embed_model import EmbedModel

meme_path: str = "databases/memes"
heads: str = "https://i.imgur.com/dTNbMle.png"
tails: str = "https://i.imgur.com/Suza17V.png"
add_meme_msg: str = "I added this new meme"


async def flip_coin(ctx: commands.Context):
    model: EmbedModel = EmbedModel("coin")
    model.set_title("HEADS")
    model.set_image(heads)

    if randint(1, 100) % 2 != 0:
        model.set_title("TAILS")
        model.set_image(tails)

    embed: Embed = embeds.create_embed(model)
    await ctx.send(embed=embed)


async def add_meme(ctx: commands.Context, args):
    if len(args) == 0:
        await ctx.send("You did not provide a meme image link.")
    elif url.is_image(args[0]):
        with open(meme_path, "a") as f:
            f.write("\n" + args[0])
        embed_model: EmbedModel = EmbedModel("NewMeme")
        embed_model.set_image(args[0])
        embed: Embed = embeds.create_embed(embed_model)
        await ctx.send(embed=embed)
        await ctx.send(add_meme_msg)
    else:
        await ctx.send("That is not a valid image url.")


def get_random_meme():
    with open(meme_path, "r") as f:
        seed()
        return choice(f.readlines())
