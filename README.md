# Hero Bot

This is a Discord bot written in Python for the Hero Smashcord server. It handles moderation, hands out mini
medals, keeps track of the server's boosters, posts memes and combo gifs, and lets admins add their own
commands without touching the code. The data is stored in SQLite databases. Every command starts with `?`.

## Features

### Moderation

`?kick`, `?ban`, `?warn`, and `?mute` all take a ping and a reason. Each one asks for a confirmation
reaction first, DMs the user why it happened, and saves the infraction to the database. `?history <user>`
sends everything that user has been given. `?unmute` takes the Snooze role back off.

The mute role is called Snooze. `?addmute` sets its permissions on every channel in the server, and the bot
does the same thing automatically whenever a new channel is created, so a muted user cannot just move
somewhere else. `?slowmode <seconds>` sets the slowmode on the current channel.

### Mini Medals

`?givemedal <user>` and `?removemedal <user>` change a user's medal count. `?medals` shows your own count,
or someone else's if you ping them, and `?medalboard` sends a top 10 leaderboard. Giving and removing
medals is admin only.

### Custom Commands

`?addcmd <name> <text>` creates a text command, and `?addcmd embed <name> <fields>` creates an embed
command. Running `?addcmd` on a command that already exists will update it, and `?removecmd <name>` will
delete it. Custom commands are checked before the built in ones, so they work the same way. Both of these
commands are admin only.

### Combos

`?combo` lists the combo starters it knows about and lets you build a combo one move at a time by reacting
with the number of the move you want. Once there are no follow ups left, the bot sends the gif for that
combo. You get 20 seconds to pick each move, and only the person who ran the command can pick.

### Boosts

`?boostboard` sends a top 10 leaderboard of the users who have been boosting the server the longest.
`?boost` gives boosters a shoutout, and everyone else gets dabbed on.

### Welcome Messages

`?welcome <message>` makes the current channel the welcome channel and sets the message. After that, anyone
who joins the server gets pinged there with it. Each server gets its own message and channel. This command
is admin only.

### Fun

`?meme` sends a random meme. `?addmeme <url>` adds a new one, but only if the url actually points to an
image, and `?removememe <url>` takes one back out. `?coin` flips a coin and `?roll <sides>` rolls a die
with however many sides you ask for.

### Help

`?info` sends a list of every command, grouped by category. `?info <command>` sends the description, usage,
and examples for that command.

Note: The channel id for the "IT'S HERO TIME" post is hardcoded in `hero/cogs/fun.py`, so you will need to
change that if you want to run this on another server.

## Setup

This bot requires a file named `secret.py` in the root folder with the following content:

```
token = "PASTE_YOUR_BOT_TOKEN_HERE"
```

The bot needs the Server Members intent turned on in the Developer Portal, since it uses member joins for
the welcome messages.

## Dependencies

- `python 3.8`

### Python Dependencies

- `discord.py 1.5.0`
- `requests`

Note: The `requirements.txt` in this repo is a full freeze of the machine it was written on, so it has a lot
more in it than the bot actually uses.

## Run

`python3 herobot.py`
