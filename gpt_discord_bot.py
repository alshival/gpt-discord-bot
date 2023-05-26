########################################################################
# This script creates a basic GPT discord bot using SQLite3 for memory storage
########################################################################
# Define setup variables here
epochs = 25
prompt_table_cache_size = 200
########################################################################

import discord
from discord.ext import commands
import openai
import asyncio
import sqlite3
import aiosqlite
import os

# Set up the OpenAI API
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Set up the bot
bot = commands.Bot(command_prefix="!",intents=discord.Intents.all())

#-----------------------------------------------------------------------
# This function establishes a global connection to the 'data.db' SQLite database.
# It is used by the other functions whenever they need to interact with the database.
async def create_connection():
    return await aiosqlite.connect('data.db')

#-----------------------------------------------------------------------
# This function creates a table named 'prompts' in the SQLite database 'data.db' upon bot startup.
# The table is used to store the bot's conversation history.
# The table has fields for id, username, prompt, model, response, channel_name, and timestamp.
async def create_table():
    # Connect to the SQLite3 database named 'data.db'
    conn = await aiosqlite.connect('data.db')
    cursor = await conn.cursor()

    # Create the 'prompts' table if it doesn't already exist
    await cursor.execute('''CREATE TABLE IF NOT EXISTS prompts
                  (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT NOT NULL,
                  prompt TEXT NOT NULL,
                  model TEXT,
                  response TEXT,
                  channel_id TEXT,
                  channel_name TEXT,
                  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

    # Commit the changes and close the connection
    await conn.commit()
    await conn.close()
    
# The 'create_table' function is called using the asyncio event loop when the bot starts up.
asyncio.get_event_loop().run_until_complete(create_table())
#-----------------------------------------------------------------------
# This function is used to fetch past conversations from the 'prompts' table.
# It fetches a set number of past prompts and responses from a specific channel.
# The 'limit' parameter determines how many past conversations to fetch.
async def fetch_prompts(db_conn, channel_name, limit):
    async with db_conn.cursor() as cursor:
        await cursor.execute('SELECT prompt, response FROM prompts WHERE channel_name = ? ORDER BY timestamp DESC LIMIT ?', (channel_name, limit,))
        return await cursor.fetchall()
#-----------------------------------------------------------------------
# This function ensures the bot's memory usage remains low by maintaining a maximum of prompt_table_cache_size responses in the database.
# It deletes the oldest entries if the count exceeds prompt_table_cache_size.
# This function is also called upon bot startup.
# You can customize the maximum number of entries by changing the 'max_rows' variable.
async def update_cache():
    # Connect to the SQLite3 database named 'data.db'
    conn = await aiosqlite.connect('data.db')
    cursor = await conn.cursor()
    
    # Fetch the total number of entries in the 'prompts' table
    await cursor.execute('SELECT COUNT(*) FROM prompts')
    count = (await cursor.fetchall())[0][0]
    max_rows = prompt_table_cache_size 

    # Delete the oldest entries if the total count exceeds the maximum limit
    if count >= max_rows:
        delete_count = count - max_rows - 1  # Calculate how many entries to delete
        await cursor.execute(f'DELETE FROM prompts WHERE id IN (SELECT id FROM prompts ORDER BY timestamp ASC LIMIT {delete_count})')
        await conn.commit()  # Commit the changes

    # Close the database connection
    await conn.close()

# The 'update_cache' function is called using the asyncio event loop when the bot starts up.
asyncio.get_event_loop().run_until_complete(update_cache())


# Define a command
@bot.command()
async def davinci3(ctx, *, prompt):
    # Generate a response using GPT
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.7,
    )

    # Send the response back to the user
    await ctx.send(response.choices[0].text)

# Define a command
@bot.command()
async def gpt3(ctx, *, message):
    db_conn = await create_connection()
    
    past_prompts = await fetch_prompts(db_conn, channel_name, 4)  # Fetch the last 4 prompts and responses

    # Construct the messages parameter with the past prompts and responses and the current message
    for prompt, response in past_prompts:
        messages.extend([{'role': 'user', 'content': prompt}, {'role': 'assistant', 'content': response}])
    messages.append({'role': 'user', 'content': message})

    # Generate a response using the 'gpt-3.5-turbo' model
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        max_tokens=1024,
        n=1,
        temperature=0.5,
        top_p=1,
        frequency_penalty=0.0,
        presence_penalty=0.6,
    )

    # Extract the response text and send it back to the user
    response_text = response['choices'][0]['message']['content']
    await ctx.send(response_text)

    # Store the new prompt and response in the 'prompts' table
    await store_prompt(db_conn, username, message, model, response_text, channel_name)
    await db_conn.close()
    
@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

# Start the bot
bot.run(os.environ.get("DISCORD_BOT_TOKEN"))


