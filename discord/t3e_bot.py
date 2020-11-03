#Discord bot for t3e

import threading
import asyncio
import logging
import random
import time
import os

import discord
from discord.ext import commands

import sys
sys.path.append('..')
import t3e

bot = commands.Bot('t3e ')
bot.remove_command('help')

################################################################################

class game_obj:
    def __init__(self, ctx):
        self.channel = ctx.channel
        self.host = ctx.author
        self.client = None
        self.buffer = ''
        self.player_X = None
        self.player_O = None
        self.player_a = None
        self.active_time = time.time()
        self.io_h = t3e.io_handler(use_secondary = True)
        self.game_thread = threading.Thread(target = t3e.main,
                                            args = (self.io_h, self.get_p_count(ctx)))
    def get_p_count(self, ctx):
        if isinstance(ctx.channel, discord.abc.PrivateChannel):
            return 1
        else:
            return 2
    def process_output(self, str):
        if str[8] == '|' and str[16] == '|':
            return '```' + str + '```'
        for index, char in enumerate(str):
            if char == 'X' or char == 'O' and str[index + 1] == '\'':
                if char == 'X':
                    self.player_a = self.player_X
                else:
                    self.player_a = self.player_O
                if self.player_a is not None:
                    return str[:index] + f'{self.player_a.mention}' + str[index + 1:-1]
                else:
                    return str[:index] + f'AI' + str[index + 1:-1]
        if str[-1:] == ':':
            return str[:-1] + '.'
        return str

    async def call_revert(self):
        self.io_h.send('KBI', primary = False)
        self.io_h.send('1', primary = False)
        await self.get_output()
    async def start_game(self):
        self.player_a = self.host
        self.game_thread.start()
        await self.get_output()
    async def get_output(self):
        intake = self.io_h.get(primary = True).split('"')
        content = intake[1]
        while intake[0].strip() == 'INF':
            if content.startswith('Waiting for'):
                break
            else:
                self.buffer += content + '\n'
            intake = self.io_h.get(primary = True).split('"')
            content = self.process_output(intake[1])
        if self.buffer != '':
            await self.channel.send(self.buffer)
            self.buffer = ''
        await self.channel.send(content)
    async def send_input(self, ctx, intake):
        self.active_time = time.time()
        if ctx.author == self.player_a:
            self.io_h.send(intake, primary = False)
            await self.get_output()
        else:
            await ctx.send(f'It is not your turn right now.')

async def timeout_checker(games, players):
    while True:
        for id, ref in enumerate(games):
            if type(ref) is str:
                continue
            if time.time() - ref.active_time > 300:
                logging.info(f'Game {id} timed out ')
                games.pop(id)
                for _ in range(2):
                    for player in players:
                        if players[player] == id:
                            del players[player]
                            break
        await asyncio.sleep(1)

def get_guild_channel(ctx):
    return f'#{ctx.channel}, {ctx.guild}'

################################################################################

@bot.command()
async def help(ctx):
    msg = """
    ```
    For instructions on how to play the game visit https://github.com/OmG-117/tictactoe-evolved/blob/master/README.md
    Commands (prefix with "t3e"):
        host as [X or O] - Host a new lobby to play against other players
        join [game_id]   - Join the game with the given ID
        start            - Start your current game
        g [input]        - Feed data to game (eg - moves, settings etc.)
        quit             - Quit your current game
    ```
    """
    await ctx.send(msg)

@bot.command()
async def ping(ctx):
    logging.info(f'In {get_guild_channel(ctx)} - Replying to {ctx.author.name}')
    await ctx.send(f'{ctx.author.mention}')

@bot.command()
async def host(ctx):
    if ctx.author in players:
        await ctx.send(f'You are already in a game. You can quit by using "t3e quit".')
        return
    try:
        type = ctx.message.content.split(' ')[3]
        if type == 'X' or type == 'O':
            pass
        else:
            type = random.choice(['X', 'O'])
            await ctx.send(f'Invalid player type - will be random.')
    except IndexError:
        await ctx.send(f'Invalid syntax. Usage: t3e host as [X or O].')
        return
    game_id = None
    for id, val in enumerate(games):
        if val is None:
            game_id = id
            break
    if not game_id:
        game_id = len(games)
        games.append(game_obj(ctx))
    else:
        games[game_id] = game_obj(ctx)
    players[ctx.author] = game_id
    if type == 'X':
        games[game_id].player_X = ctx.author
    else:
        games[game_id].player_O = ctx.author
    logging.info(f'In {get_guild_channel(ctx)} - Initialized new game with ID {game_id}, host {ctx.author}')
    if not isinstance(ctx.channel, discord.abc.PrivateChannel):
        await ctx.send(f'{ctx.author.mention} has created a game lobby! Use "t3e join {game_id}" to join their game.')
    else:
        await ctx.send(f'Game hosted. Use "t3e start" to start playing.')
    return

@bot.command()
async def join(ctx):
    if ctx.author in players:
        await ctx.send(f'You are already in a game. You can quit by using "t3e quit".')
        return
    intake = ctx.message.content.split(' ')
    logging.debug(f'In {get_guild_channel(ctx)} - Got request to join game {intake[2]}')
    try:
        game_id = int(intake[2])
        if games[game_id] is not None:
            game_ref = games[int(intake[2])]
            if not game_ref.client:
                game_ref.client = ctx.author
                players[ctx.author] = game_id
                if game_ref.player_X:
                    game_ref.player_O = ctx.author
                else:
                    game_ref.player_X = ctx.author
                logging.info(f'In {get_guild_channel(ctx)} - {ctx.author} added to game {game_id}')
                await ctx.send(f'{ctx.author.mention} has joined game {game_id}!')
                await ctx.send(f'{game_ref.host.mention} {ctx.author.mention} use "t3e start" to start your game.')
            else:
                logging.debug(f'In {get_guild_channel(ctx)} - Request denied; full game')
                await ctx.send(f'That game is full and cannot be joined. You can host a new game by using "t3e host".')
        else:
            logging.debug(f'In {get_guild_channel(ctx)} - Request denied; invalid game ID')
            await ctx.send(f'No game with that ID exists. The host can check the ID of their game by using "t3e game id".')
    except ValueError:
        logging.debug(f'In {get_guild_channel(ctx)} - Request denied; invalid syntax')
        await ctx.send(f'Invalid syntax. Usage: "t3e join [game ID]".')
    return

@bot.command()
async def quit(ctx):
    logging.debug(f'In {get_guild_channel(ctx)} - {ctx.author} requested to quit game')
    if ctx.author in players:
        game_id = players[ctx.author]
        game_ref = games[game_id]
        del players[ctx.author]
        logging.info(f'In {get_guild_channel(ctx)} - {ctx.author} quit game {game_id}')
        await ctx.send(f'{ctx.author.mention} has left game {game_id}.')
        if game_ref.client is None:
            games[game_id] = None
            logging.info(f'In {get_guild_channel(ctx)} - Game {game_id} terminated')
            await ctx.send(f'Game {game_id} has ended.')
        elif game_ref.client is ctx.author:
            game_ref.client = None
            await ctx.send(f'Game {game_id} has an empty spot and can be joined using "t3e join {game_id}".')
        else:
            game_ref.host = game_ref.client
            game_ref.client = None
            await ctx.send(f'Game {game_id} is now hosted by {game_ref.host.mention} and can be joined using "t3e join {game_id}".')
    else:
        logging.debug(f'In {get_guild_channel(ctx)} - Request denied; user not in any game')
        await ctx.send(f'You are not currently in any game. Use "t3e host" or "t3e join [game ID]" to join one.')
    return

@bot.command()
async def start(ctx):
    if ctx.author in players:
        game_id = players[ctx.author]
        logging.info(f'In {get_guild_channel(ctx)} - Game {game_id} started')
        await games[game_id].start_game()
    else:
        await ctx.send(f'You are not currently in any game. Use "t3e host" or "t3e join [game ID]" to join one.')
    return

@bot.command()
async def g(ctx):
    if ctx.author in players:
        game_id = players[ctx.author]
        intake = ctx.message.content.split(' ', maxsplit = 2)[2]
        if  intake == 'revert':
            await games[game_id].call_revert()
        else:
            await games[game_id].send_input(ctx, intake)
    else:
        await ctx.send(f'You are not currently in any game. Use "t3e host" or "t3e join [game ID]" to join one.')
    return

################################################################################

@bot.event
async def on_message(ctx):
    if ctx.author == bot.user:
        return
    await bot.process_commands(ctx)

@bot.event
async def on_ready():
    logging.info('Logged in successfully')
    await bot.change_presence(activity = discord.Game(name = 't3e help'))

################################################################################

if __name__ == '__main__':
    logging.basicConfig(format = '%(levelname)s:%(name)s:(%(asctime)s): %(message)s',
                        datefmt = '%d-%b-%y %H:%M:%S',
                        level = logging.INFO)

    logging.info('Starting initialization')

    token = ''
    authorized_players = []
    games = ['deletion guard']
    players = {'deletion guard': None}

    if token == '':
        try:
            file = open('token.txt')
            token = file.read()
            file.close()
            logging.info('Token acquired from file')
        except FileNotFoundError:
            logging.warning('Token file not found')
            try:
                token = os.environ['TOKEN']
                logging.info('Token acquired from environment variable')
            except KeyError:
                logging.warning('Token environment variable not found')
                logging.error('Token auto detection failed. Stopping execution.')
                exit()
    else:
        logging.info('Token acquired from code')

    bot.loop.create_task(timeout_checker(games, players))
    logging.info('Timeout checker started')

    logging.info('Initialization complete')

    try:
        bot.run(token)
    except OSError:
        logging.error('Connection failed')
