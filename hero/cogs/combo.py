from typing import List
from re import findall
from os import path

from discord import Message, Embed
from discord.ext import commands

from hero.utils import reactions, embeds
from hero.utils.embed_model import EmbedModel

# TODO: this is literally a text file, will need a table for this some day
combo_dir = "databases/combos"
combo_msg: str = "Pick a move for the combo within 20 seconds (Sender Only):\n```{}```"


class Combo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="combo")
    async def combo(self, ctx: commands.Context):
        if not path.exists(combo_dir):
            open(combo_dir, "w+")
        combo_links: List[str] = self.load_combos()
        if len(combo_links) == 0:
            await ctx.send("There are no combos.")
            return
        combos: dict = self.parse_combo_links(combo_links)
        final_combo: str = await self.get_combo(ctx, combos)
        if not final_combo:
            return
        for c in combo_links:
            if final_combo + ".gif" == str(c.split("/")[-1]):
                model: EmbedModel = EmbedModel("combo")
                model.set_title(final_combo)
                model.set_image(c)
                embed: Embed = embeds.create_embed(model)
                await ctx.send(embed=embed)
                break

    def load_combos(self):
        combo_files: List[str] = []
        with open(combo_dir, "r") as combo_file:
            links: List[str] = combo_file.readlines()
            for link in links:
                combo_files.append(str.rstrip(link))
        return combo_files

    def parse_combo_links(self, links: list):
        combos: dict = {}
        for link in links:
            f: str = link.split("/")[-1]
            combo: List[str] = findall('[A-Z][^A-Z]*', f.split(".")[0])
            if combo[0] in combos.keys():
                combos[combo[0]].append(combo[1:])
            else:
                combos[combo[0]] = [combo[1:]]
        return combos

    # TODO: Can probably make this better with recursion
    async def get_combo(self, ctx: commands.Context, combos: dict):
        final_combo: str = ""
        resp: Message = None
        while True:
            msg: str = ""
            moves = list(combos.keys())
            for i, move in enumerate(moves):
                msg += "\n {}. {}".format(i + 1, move)

            if not resp:
                resp = await ctx.send(combo_msg.format(msg))
            else:
                await resp.clear_reactions()
                await resp.edit(content=combo_msg.format(msg))

            c: int = await reactions.move_selection(ctx, resp, len(moves))
            if c == -1:
                await resp.edit(content="You took too long to select a move.")
                await resp.clear_reactions()
                return ""

            move: str = moves[c]
            final_combo += move
            follow_ups: List[str] = combos[move]
            combos = {}

            if len(follow_ups) == 1:
                final_combo += "".join(follow_ups[0])
                break

            for combo in follow_ups:
                first_move = combo[0]
                if first_move in combos.keys() and len(combo) > 1:
                    combos[first_move].append(combo[1:])
                elif first_move in combos.keys():
                    combos[first_move].append(combo)
                else:
                    combos[first_move] = [combo[1:]]

        await resp.delete()
        return final_combo
