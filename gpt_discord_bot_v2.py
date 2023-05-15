########################################################################
# This version of the bot has memory. It'll remember past conversations.
# It uses a SQLite3 database to do so.
########################################################################
import discord
from discord.ext import commands
import openai
import os
import sqlite3
import aiosqlite
import asyncio

# Set up the OpenAI API
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Set up the bot
bot = commands.Bot(command_prefix="!",intents=discord.Intents.all())

# Create the 'prompts' table
async def create_table():
    # Connect to the database
    conn = await aiosqlite.connect('data.db')
    cursor = await conn.cursor()

    # Create the table if it doesn't exist
    await cursor.execute('''CREATE TABLE IF NOT EXISTS prompts
                  (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  prompt TEXT NOT NULL,
                  model TEXT,
                  response TEXT,
                  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

    # Commit the changes and close the connection
    await conn.commit()
    await conn.close()

# Call the async function using an event loop
asyncio.get_event_loop().run_until_complete(create_table())

# This function is what gives our bot memory:
# Fetch the last few prompts and responses
async def fetch_prompts(db_conn, limit):
    async with db_conn.cursor() as cursor:
        await cursor.execute('SELECT prompt, response FROM prompts ORDER BY timestamp DESC LIMIT ?', (limit,))
        return await cursor.fetchall()
############################################################
# In order to keep the memory low, we keep only 200 responses.
# Every time the bot boots up, it'll check this.
# You can edit or comment out this part if you wish.
# Get the number of prompts in the table
def update_cache():
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    
    count = cursor.execute('SELECT COUNT(*) FROM prompts').fetchall()[0][0]
    # Check if the count exceeds 200
    max_rows = 200

    if count >= max_rows:
        # Calculate the number of prompts to delete
        delete_count = count - max_rows - 1  # Keep a maximum of max_rows prompts

        # Delete the oldest prompts
        cursor.execute(f'DELETE FROM prompts WHERE id IN (SELECT id FROM prompts ORDER BY timestamp ASC LIMIT {delete_count})')
        # commit the changes and close the connection
        conn.commit()
        conn.close()

update_cache()
############################################################


# Create a global database connection
async def create_connection():
    return await aiosqlite.connect('data.db')

async def store_prompt(db_conn, prompt,model,response):
    async with db_conn.cursor() as cursor:
        await cursor.execute('INSERT INTO prompts (prompt,model,response) VALUES (?, ?, ?)', (prompt,model, response))
        await db_conn.commit()
        

# Define a command. 
@bot.command()
async def chatGPT(ctx, *, prompt):
    model = "text-davinci-002"
    
    db_conn = await create_connection()
    past_prompts = await fetch_prompts(db_conn, 4)  # fetch the last 4 prompts and responses

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
    
    # Store the new prompt and response
    await store_prompt(db_conn, prompt, model, response_text)
    await db_conn.close()

# Define a command
# Define a command
@bot.command()
async def chatGPTturbo(ctx, *, message):
    # Generate a response using GPT
    model = "gpt-3.5-turbo"
    
    db_conn = await create_connection()
    past_prompts = await fetch_prompts(db_conn, 4)  # fetch the last 4 prompts and responses

    # Construct the messages parameter with the past prompts and responses and the current message
    messages = []
    for prompt, response in past_prompts:
        messages.extend([{'role': 'user', 'content': prompt}, {'role': 'assistant', 'content': response}])
    messages.append({'role': 'user', 'content': message})

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
    
    # Send the response back to the user
    response_text = response['choices'][0]['message']['content']
    await ctx.send(response_text)

    # Store the new prompt and response
    await store_prompt(db_conn, message, model, response_text)
    await db_conn.close()
    
# Start the bot
bot.run(os.environ.get("DISCORD_BOT_TOKEN"))