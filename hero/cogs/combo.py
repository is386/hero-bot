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

    # Displays an embed with a combo gif
    @commands.command(name="combo")
    async def combo(self, ctx: commands.Context):
        if not path.exists(combo_dir):
            open(combo_dir, "w+")
        combo_links: List[str] = self.load_combos()
        if len(combo_links) == 0:
            await ctx.send("There are no combos.")
            return

        # Extracts the full combo names from the gif links
        combos: dict = self.parse_combo_links(combo_links)

        # Gets the name of the combo the user wants
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

    # Loads the combo gif links from the file
    def load_combos(self) -> List[str]:
        combo_files: List[str] = []
        with open(combo_dir, "r") as combo_file:
            links: List[str] = combo_file.readlines()
            for link in links:
                combo_files.append(str.rstrip(link))
        return combo_files

    # Extracts the combo name from each link and returns a dict
    # Dict's keys are combo starters, and values are list of moves that follow that starter
    # Example {nair: [[bair, uair], [uair, nair, nair]]}
    def parse_combo_links(self, links: list) -> dict:
        combos: dict = {}
        for link in links:
            f: str = link.split("/")[-1]
            combo: List[str] = findall('[A-Z][^A-Z]*', f.split(".")[0])
            if combo[0] in combos.keys():
                combos[combo[0]].append(combo[1:])
            else:
                combos[combo[0]] = [combo[1:]]
        return combos

    # TODO: Should probably use recursion to make this better
    # Returns the name of the combo the user chose
    async def get_combo(self, ctx: commands.Context, combos: dict) -> str:
        final_combo: str = ""
        resp: Message = None
        # Works down the combo tree (dict) until there are no more follow up moves
        while True:
            msg: str = ""
            # Gets a list of moves the user can choose from. This is either
            # a combo starter or the next move in the combo path they are
            # going through
            moves = list(combos.keys())
            for i, move in enumerate(moves):
                msg += "\n {}. {}".format(i + 1, move)

            # Sends a list of moves for the user to pick from
            if not resp:
                resp = await ctx.send(combo_msg.format(msg))
            # If the first message is already sent, it just edits it with new moves
            else:
                await resp.clear_reactions()
                await resp.edit(content=combo_msg.format(msg))

            # Waits for the user to pick the next move in the combo
            c: int = await reactions.move_selection(ctx, resp, len(moves))
            if c == -1:
                await resp.edit(content="You took too long to select a move.")
                await resp.clear_reactions()
                return ""

            # Gets the move the user choice
            move: str = moves[c]

            # Adds the move to the final combo
            final_combo += move

            # Gets all the follow up combos for the chosen move
            follow_ups: List[str] = combos[move]
            combos = {}

            # If there is only 1 follow up, then that is the combo to send
            if len(follow_ups) == 1:
                final_combo += "".join(follow_ups[0])
                break

            # Goes through every follow up
            # This basically does what part of parse_combo_links does
            # TODO: Make a function for this
            for f in follow_ups:
                first_move = f[0]
                if first_move in combos.keys() and len(f) > 1:
                    combos[first_move].append(f[1:])
                elif first_move in combos.keys():
                    combos[first_move].append(f)
                else:
                    combos[first_move] = [f[1:]]

        await resp.delete()
        return final_combo
