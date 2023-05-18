import discord
from discord.ext import commands,tasks
import openai
import os
from datetime import datetime, timedelta
import sqlite3
import aiosqlite
import asyncio
import json

# Set up the OpenAI API. The key is stored as an environment variable for security reasons. 
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Set up the bot with '!' as the command prefix. 
# It is set to listen and respond to all types of intents in the server. 
# You can change the command prefix by replacing '!' with your preferred symbol.
bot = commands.Bot(command_prefix="!",intents=discord.Intents.all())
import random

my_dict = {
    0: {'member': 'author1', 'emoji': 'O', 'mention': 'p1'},
    1: {'member': 'author2', 'emoji': 'X', 'mention': 'p2'}
}

# Convert dictionary items to a list
items = list(my_dict.items())

# Shuffle the list randomly
random.shuffle(items)

# Create a new dictionary from the shuffled list
shuffled_dict = dict(items)

@bot.command()
async def gptttt(ctx):
    # Initial empty board
    board = [
        [None, None, None],
        [None, None, None],
        [None, None, None]
    ]
    def check_win(board):
        win_conditions = [
            [board[0][0], board[0][1], board[0][2]],
            [board[1][0], board[1][1], board[1][2]],
            [board[2][0], board[2][1], board[2][2]],
            [board[0][0], board[1][0], board[2][0]],
            [board[0][1], board[1][1], board[2][1]],
            [board[0][2], board[1][2], board[2][2]],
            [board[0][0], board[1][1], board[2][2]],
            [board[0][2], board[1][1], board[2][0]]
        ]

        if ['O', 'O', 'O'] in win_conditions:
            return 'O'
        elif ['X', 'X', 'X'] in win_conditions:
            return 'X'
        return None

    def print_board(board):
        emojis = {None: ":white_large_square:", 'X': ":regional_indicator_x:", 'O': ":o2:"}
        return "\n".join(["".join(emojis[i] for i in row) for row in board])
    
    players = [{'member':ctx.author.name,'mention':ctx.author.mention},{'member':'chatGPT','mention':'chatGPT'}]
    random.shuffle(players)
    emoji_to_players = dict(zip(['O','X'],players))
    players = {0: {'member': emoji_to_players['O']['member'], 'emoji': 'O', 'mention': emoji_to_players['O']['mention']}, 
                1: {'member': emoji_to_players['X']['member'], 'emoji': 'X', 'mention': emoji_to_players['X']['mention']}}
    
    async def bot_move(players,board):
        bot_emoji = [p['emoji'] for p in players.values() if p['mention'] == 'chatGPT']
        
        game_train = [
            {
            'role':'user',
            'content': """ 
                You are X. Make a move.
                [['X', 'O', 'O'],['X', None, 'X'],[None, 'X', 'O']]
                """
            },{
            'role':'assistant',
            'content': "[['X', 'O', 'O'],['X', None, 'X'],['X', 'X', 'O']]"
            },
            {
            'role':'user',
            'content': """ 
                You are O. Make a move. [[None, 'O', 'X'], ['O', None, 'X'], ['X', 'O', None]]
                """
            },{
            'role':'assistant',
            'content': "[[None, 'O', 'X'], ['O', None, 'X'], ['X', 'O', 'O']]"
            },
            {
            'role':'user',
            'content': """ 
                You are X. Make a move. [['X', 'X', 'O'], ['O', None, None], ['X', None, 'O']]
                """
            },{
            'role':'assistant',
            'content': "[['X', 'X', 'O'], ['O', None, 'X'], ['X', None, 'O']]"
            },
            {
            'role':'user',
            'content': """You are O. Make a move. [[None, 'O', None], ['X', 'O', 'X'], ['O', None, 'X']]"""
            },{
            'role':'assistant',
            'content': "[[None, 'O', None], ['X', 'O', 'X'], ['O', 'O', 'X']]"
            },
            {
            'role':'user',
            'content':f"""
                You are {bot_emoji}. Make a move. {board}
            """
            }
        ]

        
        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=game_train,
            max_tokens=1024,
            n=1,
            temperature=0.5,
            top_p=1,
            frequency_penalty=0.0,
            presence_penalty=0.6,
        )
        
        board = response['choices'][0]['message']['content']
        board = eval(board)
        return board
    
    winner = None
    turns = range(0,9)
    for turn in turns:
        current_player = players[turn % 2]
        if current_player['mention'] == 'chatGPT':
            board = await bot_move(players,board)
            await ctx.send(print_board(board))            
            turn += 1
        else:
            await ctx.send(f"{current_player['mention']}'s turn!")
            msg = await bot.wait_for("message", check=lambda message: message.author.name == current_player['member'])
            try:
                row, col = [int(pos) for pos in msg.content.split()]
                if board[row][col] is None:
                    board[row][col] = current_player['emoji']
                    await ctx.send(print_board(board))
                else:
                    await ctx.send("Invalid move! You lose your turn.")
            except Exception as e:
                await ctx.send("Invalid input! Please send your move in format 'row col'. For example, '2 1' for the middle square on the last row. You lose your turn.")
            turn += 1
        winner = check_win(board)
        if winner:
            await ctx.send(f"{current_player['mention']} wins!")
            return
        if not any(None in row for row in board):
            await ctx.send("Game over! It's a draw.")
            return

bot.run(os.environ.get("DISCORD_BOT_TOKEN"))
