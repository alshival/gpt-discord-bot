########################################################################
# This script creates a Discord bot that interacts with users using 
# OpenAI's GPT models. It keeps a history of its past conversations,
# allowing it to generate responses based on previous interactions. 
# This script should be customized as per the user's requirements.
# It utilizes the OpenAI API and SQLite3 database to store and retrieve 
# past conversations. 
########################################################################

import discord
from discord.ext import commands
import openai
import os
import sqlite3
import aiosqlite
import asyncio

# Set up the OpenAI API. The key is stored as an environment variable for security reasons. 
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Set up the bot with '!' as the command prefix. 
# It is set to listen and respond to all types of intents in the server. 
# You can change the command prefix by replacing '!' with your preferred symbol.
bot = commands.Bot(command_prefix="!",intents=discord.Intents.all())


########################################################################
# Boot Sequence for the Bot
########################################################################
# This function creates a table named 'prompts' in the SQLite database 'data.db' upon bot startup.
# The table is used to store the bot's conversation history.
# The table has fields for id, user_id, prompt, model, response, channel_name, and timestamp.
async def create_table():
    # Connect to the SQLite3 database named 'data.db'
    conn = await aiosqlite.connect('data.db')
    cursor = await conn.cursor()

    # Create the 'prompts' table if it doesn't already exist
    await cursor.execute('''CREATE TABLE IF NOT EXISTS prompts
                  (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER NOT NULL,
                  prompt TEXT NOT NULL,
                  model TEXT,
                  response TEXT,
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
# This function ensures the bot's memory usage remains low by maintaining a maximum of 200 responses in the database.
# It deletes the oldest entries if the count exceeds 200.
# This function is also called upon bot startup.
# You can customize the maximum number of entries by changing the 'max_rows' variable.
async def update_cache():
    # Connect to the SQLite3 database named 'data.db'
    conn = await aiosqlite.connect('data.db')
    cursor = await conn.cursor()
    
    # Fetch the total number of entries in the 'prompts' table
    await cursor.execute('SELECT COUNT(*) FROM prompts')
    count = (await cursor.fetchall())[0][0]
    max_rows = 200  # Change this value to customize the maximum number of entries.

    # Delete the oldest entries if the total count exceeds the maximum limit
    if count >= max_rows:
        delete_count = count - max_rows - 1  # Calculate how many entries to delete
        await cursor.execute(f'DELETE FROM prompts WHERE id IN (SELECT id FROM prompts ORDER BY timestamp ASC LIMIT {delete_count})')
        await conn.commit()  # Commit the changes

    # Close the database connection
    await conn.close()

# The 'update_cache' function is called using the asyncio event loop when the bot starts up.
asyncio.get_event_loop().run_until_complete(update_cache())

#-----------------------------------------------------------------------
# This function establishes a global connection to the 'data.db' SQLite database.
# It is used by the other functions whenever they need to interact with the database.
async def create_connection():
    return await aiosqlite.connect('data.db')

# This function is used to store a new conversation in the 'prompts' table.
# It inserts a new row with the user_id, prompt, model, response, and channel_name into the table.
async def store_prompt(db_conn, user_id, prompt, model, response, channel_name):
    async with db_conn.cursor() as cursor:
        await cursor.execute('INSERT INTO prompts (user_id, prompt, model, response, channel_name) VALUES (?, ?, ?, ?, ?)', (user_id, prompt, model, response, channel_name))
        await db_conn.commit()

########################################################################
# Discord Commands Definition
########################################################################
# The bot responds to two commands: '!chatGPT' and '!chatGPTturbo'.
# You can customize the names of these commands by changing the names in the '@bot.command()' decorators.
#-----------------------------------------------------------------------
# The '!chatGPT' command generates a response using the 'text-davinci-002' model.
# It fetches the last four prompts and responses from the database, and then generates a new response.
@bot.command()
async def chatGPT(ctx, *, prompt):
    model = "text-davinci-002"
    
    db_conn = await create_connection()
    user_id = ctx.author.id
    
    channel_name = ctx.channel.name
    past_prompts = await fetch_prompts(db_conn, model, 4)  # Fetch the last 4 prompts and responses

    # Construct the messages parameter with the past prompts and responses and the current message
    messages = []
    for promp, response in past_prompts:
        messages.extend([{'role': 'user', 'content': promp}, {'role': 'assistant', 'content': response}])
    messages.append({'role': 'user', 'content': prompt})

    # Generate a response using GPT
    response = openai.Completion.create(
        engine=model,
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.7,
    )
    # Send the response back to the user
    response_text = response.choices[0].text
    await ctx.send(response_text)

    # Store the new prompt and response in the 'prompts' table
    await store_prompt(db_conn, user_id, prompt, model, response_text, channel_name)
    await db_conn.close()
#-----------------------------------------------------------------------
# The '!chatGPTturbo' command generates a response using the 'gpt-3.5-turbo' model.
# Similar to the '!chatGPT' command, it fetches the last four prompts and responses, and then generates a new response.
@bot.command()
async def chatGPTturbo(ctx, *, message):
    model = "gpt-3.5-turbo"
    
    db_conn = await create_connection()
    user_id = ctx.author.id
    
    channel_name = ctx.channel.name
    past_prompts = await fetch_prompts(db_conn, model, 4)  # Fetch the last 4 prompts and responses

    # Construct the messages parameter with the past prompts and responses and the current message
    messages = []
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
    await store_prompt(db_conn, user_id, message, model, response_text, channel_name)
    await db_conn.close()

########################################################################
# Bot Startup Sequence
########################################################################
# This command starts the bot using the DISCORD_BOT_TOKEN environment variable.
# You must replace "DISCORD_BOT_TOKEN" with your actual discord bot token.
bot.run(os.environ.get("DISCORD_BOT_TOKEN"))
