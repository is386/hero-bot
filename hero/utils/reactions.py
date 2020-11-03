from typing import List
from asyncio import TimeoutError
from discord import Message, User
from discord.ext.commands import Context

timeout = 20.0
red_circle: str = "🔴"
number_emojis: List[str] = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣',
                            '7️⃣', '8️⃣', '9️⃣', '🔟', '🇦', '🇧',
                            '🇨', '🇩', '🇪', '🇫']


# Waits for the user to press the red button reaction to proceed
async def confirm(ctx: Context, resp: Message) -> bool:
    await resp.add_reaction(red_circle)
    try:
        # This loop prevents a bug where if you did two stats cmds and reacted to one of them,
        # it would send the follow up message to both messages instead of the one that was reacted to.
        while True:
            await ctx.bot.wait_for('reaction_add',
                                   timeout=timeout,
                                   check=lambda react, user: str(react.emoji) == red_circle and user == ctx.author)

            resp = await ctx.channel.fetch_message(resp.id)
            if resp.reactions[0].count > 1:
                return True

    except TimeoutError:
        return False


# Waits for a user to pick a move from a list of moves via reactions
async def move_selection(ctx: Context, resp: Message, emoji_count: int) -> int:
    for i in range(emoji_count):
        await resp.add_reaction(number_emojis[i])

    try:
        # This loop prevents a bug where if you did two stats cmds and reacted to one of them,
        # it would send the follow up message to both messages instead of the one that was reacted to.
        while True:
            await ctx.bot.wait_for('reaction_add',
                                   timeout=timeout,
                                   check=lambda react, user: str(react.emoji) in number_emojis and user == ctx.author)

            resp = await ctx.channel.fetch_message(resp.id)
            # Updates the response sent earlier with the newly added reactions.
            for reaction in resp.reactions:
                users: List[User] = await reaction.users().flatten()
                if reaction.count > 1 and ctx.author in users:
                    n: int = number_emojis.index(reaction.emoji)
                    return n
    except TimeoutError:
        return -1
