from typing import List
from sqlite3 import Connection

from discord import Game, Embed, Message, Intents
from discord.ext import commands

from secret import token
from hero.utils.embed_model import EmbedModel
from hero.utils import embeds, cmd_database

from hero.cogs.boost import Boost
from hero.cogs.combo import Combo
from hero.cogs.custom import CustomCommands
from hero.cogs.fun import Fun
from hero.cogs.help import Help
from hero.cogs.medals import Medals
from hero.cogs.mod import Mod
from hero.cogs.welcome import Welcome

prefix: str = "?"
status_msg: str = "Type ?info"
intents = Intents.default()
intents.members = True
bot: commands.Bot = commands.Bot(
    command_prefix=prefix,
    help_command=None,
    activity=Game(status_msg),
    intents=intents)


@bot.event
async def on_message(msg: Message):
    if bot.user == msg.author or len(msg.content) == 0 or msg.content[0] != prefix:
        return

    cmd: str = msg.content.split()[0][1:]
    cmd_db: Connection = cmd_database.connect_to_cmd_db()
    text_cmds: List = cmd_database.select_all_text_cmds(cmd_db)
    embed_cmds: List = cmd_database.select_all_embed_cmds(cmd_db)

    if cmd in text_cmds:
        text: str = cmd_database.select_text_cmd(cmd, cmd_db)
        await msg.channel.send(text)
        return
    elif cmd in embed_cmds:
        embed_model: EmbedModel = embeds.get_embed_model(cmd)
        embed: Embed = embeds.create_embed(embed_model)
        await msg.channel.send(embed=embed)
        return

    await bot.process_commands(msg)


bot.add_cog(Boost(bot))
bot.add_cog(Combo(bot))
bot.add_cog(CustomCommands(bot))
bot.add_cog(Fun(bot))
bot.add_cog(Help(bot))
bot.add_cog(Medals(bot))
bot.add_cog(Mod(bot))
bot.add_cog(Welcome(bot))
bot.run(token)
