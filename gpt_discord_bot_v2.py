########################################################################
# This script creates a Discord bot that interacts with users using 
# OpenAI's GPT models. It keeps a history of its past conversations,
# allowing it to generate responses based on previous interactions. 
# This script should be customized as per the user's requirements.
# It utilizes the OpenAI API and SQLite3 database to store and retrieve 
# past conversations. 
########################################################################

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


########################################################################
# Keras Task Assigner
########################################################################
# This code demonstrates a simple task assigner using Keras, which classifies
# messages as either 'reminder' or 'other'. It is used before GPT in order
# to classify which type of task will be run.
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense

max_sequence_length = None
word_to_index = None
model = None

async def train_keras():
    global max_sequence_length
    global word_to_index
    global model

    # Dummy training data generated using GPT4
    messages = [
        "Remind me to pick up the kids in 45 minutes",
        "Remind me to turn in my homework at midnight",
        "What's your favorite color?",
        "Remind me to call mom at 3pm.",
        "Can you send me the report?",
        "Buy tickets for the concert",
        "Remind me to pick up some milk later.",
        "Remind us to study for the final exam next week.",
        "remind me to fix my essay in an hour.",
        "remind me to throw my shoes away in three days.",
        "About how many atoms are there in the universe?",
        "Remind me to feed the dog at 6pm.",
        "Let's play a game.",
        "Can you turn on the TV?",
        "Remind me to check my email after dinner.",
        "What's the weather like today?",
        "Remind me to take my medicine at 8am.",
        "Let's order pizza for dinner.",
        "Remind me to water the plants tomorrow morning.",
        "How many planets are there in our solar system?",
        "Remind me to book a doctor's appointment next Monday.",
        "Can you find a good recipe for spaghetti bolognese?",
        "Remind me to charge my phone.",
        "Who won the basketball game last night?",
        "Remind me to finish my online course this weekend.",
        "Can you tell me a joke?",
        "Remind me to call the plumber tomorrow.",
        "What's the capital of Australia?",
        "Remind me to renew my driver's license next month.",
        "Remind me to buy groceries on the way home.",
        "What time is it?",
        "Remind me to pick up my dry cleaning this afternoon.",
        "Who won the Oscar for Best Picture last year?",
        "Remind me to check the oven in 30 minutes.",
        "Can you recommend a good book?",
        "Remind me to schedule a team meeting for next Tuesday.",
        "What's the score of the baseball game?",
        "Remind me to fill up the car with gas tomorrow.",
        "Can you find the fastest route to the airport?",
        "Remind me to pay the electric bill by the end of the week.",
        "Who is the president of the United States?",
        "Remind me to update my resume this weekend.",
        "Can you play my favorite song?",
        "Remind me to check in for my flight 24 hours before departure.",
        "What are the ingredients in a Caesar salad?",
        "Remind me to bring my umbrella if it's going to rain tomorrow.",
        "How do you make a margarita?",
        "Remind me to pick up the kids in 45 minutes",
        "Remind me to turn in my homework at midnight",
        "What's your favorite color?",
        "Remind me to call mom at 3pm.",
        "Can you send me the report?",
        "Buy tickets for the concert",
        "Remind me to pick up some milk later.",
        "Remind us to study for the final exam next week.",
        "remind me to fix my essay in an hour.",
        "remind me to throw my shoes away in three days.",
        "About how many atoms are there in the universe?",
        "Remind me to feed the dog at 6pm.",
        "Let's play a game.",
        "Can you turn on the TV?",
        "Remind me to check my email after dinner.",
        "What's the weather like today?",
        "Remind me to take my medicine at 8am.",
        "Let's order pizza for dinner.",
        "Remind me to water the plants tomorrow morning.",
        "How many planets are there in our solar system?",
        "Remind me to book a doctor's appointment next Monday.",
        "Can you find a good recipe for spaghetti bolognese?",
        "Remind me to charge my phone.",
        "Who won the basketball game last night?",
        "Remind me to finish my online course this weekend.",
        "Can you tell me a joke?",
        "Remind me to call the plumber tomorrow.",
        "What's the capital of Australia?",
        "Remind me to renew my driver's license next month.",
        "Remind me to buy groceries on the way home.",
        "What time is it?",
        "Remind me to pick up my dry cleaning this afternoon.",
        "Who won the Oscar for Best Picture last year?",
        "Remind me to check the oven in 30 minutes.",
        "Can you recommend a good book?",
        "Remind me to schedule a team meeting for next Tuesday.",
        "What's the score of the baseball game?",
        "Remind me to fill up the car with gas tomorrow.",
        "Can you find the fastest route to the airport?",
        "Remind me to pay the electric bill by the end of the week.",
        "Who is the president of the United States?",
        "Remind me to update my resume this weekend.",
        "Can you play my favorite song?",
        "Remind me to check in for my flight 24 hours before departure.",
        "What are the ingredients in a Caesar salad?",
        "Remind me to bring my umbrella if it's going to rain tomorrow.",
        "How do you make a margarita?",
        "In a short answer, tell me how to write pi/2 as an infinite sum."
    ]
    labels = [
        'reminder','reminder','other','reminder','other',
        'other','reminder','reminder','reminder','reminder',
        'other','reminder','other','other','reminder','other',
        'reminder','other','reminder','other','reminder','other',
        'reminder','other','reminder','other','reminder','other',
        'reminder','reminder','other','reminder','other','reminder',
        'other','reminder','other','reminder','other','reminder',
        'other','reminder','other','reminder','other','reminder',
        'other','reminder','reminder','other','reminder','other',
        'other','reminder','reminder','reminder','reminder','other',
        'reminder','other','other','reminder','other','reminder','other',
        'reminder','other','reminder','other','reminder','other','reminder',
        'other','reminder','other','reminder','reminder','other','reminder',
        'other','reminder','other','reminder','other','reminder','other',
        'reminder','other','reminder','other','reminder','other','reminder',
        'other','other']


    # Preprocessing
    vocab = set(' '.join(messages).lower().split())
    vocab_size = len(vocab)
    word_to_index = {word: index for index, word in enumerate(vocab)}
    max_sequence_length = max(len(message.split()) for message in messages)

    # Convert sentences to numerical sequences
    X = np.zeros((len(messages), max_sequence_length))
    for i, message in enumerate(messages):
        words = message.lower().split()
        for j, word in enumerate(words):
            X[i, j] = word_to_index[word]

    # Convert labels to numerical values
    label_to_index = {'reminder': 0, 'other': 1}
    y = np.array([label_to_index[label] for label in labels])

    # Define the model
    model = Sequential()
    model.add(Dense(64, activation='relu', input_shape=(max_sequence_length,)))
    model.add(Dense(1, activation='sigmoid'))

    # Compile the model
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

    # Train the model
    model.fit(X, y, epochs=25, batch_size=1, verbose=1)

# Train the model when the bot starts up.
asyncio.get_event_loop().run_until_complete(train_keras())

# Classify text.
async def classify_prompt(input_string):
    global max_sequence_length
    global word_to_index
    global model

    # Preprocess the input string
    new_sequence = np.zeros((1, max_sequence_length))
    words = input_string.lower().split()
    for j, word in enumerate(words):
        if word in word_to_index:
            new_sequence[0, j] = word_to_index[word]

    # Make prediction
    prediction = model.predict(new_sequence)
    predicted_label = 'reminder' if prediction < 0.5 else 'other'

    return predicted_label

########################################################################
# Boot Sequence for the Bot
########################################################################
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
                  channel_name TEXT,
                  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

    # Commit the changes and close the connection
    await conn.commit()
    await conn.close()
    
# The 'create_table' function is called using the asyncio event loop when the bot starts up.
asyncio.get_event_loop().run_until_complete(create_table())

#-----------------------------------------------------------------------
# 'create_reminder_table' function creates a new table named 'reminders' in the SQLite database 'data.db'.
# This table is used to store reminders set by users.
# The table has fields for id, username, message, channel_name, and reminder_time.
async def create_reminder_table():
    conn = await aiosqlite.connect('data.db')
    cursor = await conn.cursor()

    await cursor.execute('''CREATE TABLE IF NOT EXISTS reminders
                  (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT NOT NULL,
                  reminder TEXT NOT NULL,
                  channel_id TEXT NOT NULL,
                  channel_name TEXT NOT NULL,
                  reminder_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

    await conn.commit()
    await conn.close()

asyncio.get_event_loop().run_until_complete(create_reminder_table())


#-----------------------------------------------------------------------
# 'create_labeled_prompts_table' function creates a new table named 'labeled_prompts' in the SQLite database 'data.db'.
# This table is used to quickly label the last channel prompt as a 'reminder' request or 'order' request. 
# Use `!label_last reminder` or `!label_last other` in Discord.

async def create_labeled_prompts_table():
    conn = await aiosqlite.connect('data.db')
    cursor = await conn.cursor()
    await cursor.execute('''CREATE TABLE IF NOT EXISTS labeled_prompts
                      (id INTEGER PRIMARY_KEY,
                      username TEXT NOT NULL,
                      prompt TEXT NOT NULL,
                      model TEXT,
                      response TEXT,
                      channel_name TEXT,
                      timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      label TEXT)''')
    await conn.commit()
    await conn.close()

asyncio.get_event_loop().run_until_complete(create_labeled_prompts_table())

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

#-----------------------------------------------------------------------
# This function is used to store a new conversation in the 'prompts' table.
# It inserts a new row with the username, prompt, model, response, and channel_name into the table.
async def store_prompt(db_conn, username, prompt, model, response, channel_name):
    async with db_conn.cursor() as cursor:
        await cursor.execute('INSERT INTO prompts (username, prompt, model, response, channel_name) VALUES (?, ?, ?, ?, ?)', (username, prompt, model, response, channel_name))
        await db_conn.commit()

#-----------------------------------------------------------------------
# 'fetch_due_reminders' function fetches all reminders that are due to be sent.
# It selects all reminders from the 'reminders' table where the reminder_time is less than or equal to the current timestamp.

async def fetch_due_reminders():
    conn = await aiosqlite.connect('data.db')
    cursor = await conn.cursor()

    await cursor.execute('SELECT id, username, reminder, channel_id, channel_name FROM reminders WHERE reminder_time <= CURRENT_TIMESTAMP')
    reminders = await cursor.fetchall()

    await conn.close()

    return reminders

#-----------------------------------------------------------------------
# 'delete_reminder' function deletes a reminder from the 'reminders' table.
# It takes the id of the reminder to be deleted as an argument.

async def delete_reminder(reminder_id):
    conn = await aiosqlite.connect('data.db')
    cursor = await conn.cursor()

    await cursor.execute('DELETE FROM reminders WHERE id = ?', (reminder_id,))
    await conn.commit()
    await conn.close()

#-----------------------------------------------------------------------
# 'add_reminder' function is used to add a new reminder to the 'reminders' table.
# It takes username, message, channel_name, and reminder_time as arguments and inserts a new row into the table.

async def add_reminder(username, reminder, channel_id, channel_name, reminder_time):
    conn = await aiosqlite.connect('data.db')
    cursor = await conn.cursor()

    await cursor.execute('INSERT INTO reminders (username, reminder, channel_id, channel_name, reminder_time) VALUES (?, ?, ?, ?, ?)',
                         (username, reminder, channel_id, channel_name, reminder_time))
    await conn.commit()
    await conn.close()
    
#----------------------------------------------------------------------
async def label_last_prompt(ctx,db_conn, label):
    async with db_conn.cursor() as cursor:
        await cursor.execute(f"""
        SELECT * FROM prompts 
        where channel_name = '{ctx.channel.name}' 
            AND username = '{ctx.author.name}'
        ORDER BY id DESC LIMIT 1
        """)
        last_row = await cursor.fetchone()
       # If last_row is not None, insert its data into 'labeled_prompts'
        if last_row is not None:
            insert_query = '''INSERT INTO labeled_prompts (id, username, prompt, model, response, channel_name, timestamp,label)
                              VALUES (?, ?, ?, ?, ?, ?, ?, ?)'''
            data_tuple = last_row + (label,)  # Add label to the tuple
            
            await cursor.execute(insert_query, data_tuple)
            await db_conn.commit()
            
# Ignore this chunk
# async def store_prompt(db_conn, username, prompt, model, response, channel_name):
#     async with db_conn.cursor() as cursor:
#         await cursor.execute('INSERT INTO prompts (username, prompt, model, response, channel_name) VALUES (?, ?, ?, ?, ?)', (username, prompt, model, response, channel_name))
#         await db_conn.commit()

########################################################################
# Discord Command Definitions
########################################################################
# The bot responds to two commands: '!davinci3' and '!gpt3'.
# You can customize the names of these commands by changing the names in the '@bot.command()' decorators.
# UPDATE: 2023-05-16 - Third function added: `!reminder YYYY-MM-DD 2:56 TAKE A BREAK!`

#-----------------------------------------------------------------------
# The '!davinci3' command generates a response using the 'text-davinci-002' model.
# It fetches the last four prompts and responses from the database, and then generates a new response.
@bot.command()
async def davinci3(ctx, *, prompt):
    model = "text-davinci-003"
    
    db_conn = await create_connection()
    username = ctx.author.name
    
    channel_name = ctx.channel.name
    # Past prompts not compatible with openai.Completion.create, 
    # which is used to call `text-davinci-002`
    # past_prompts = await fetch_prompts(db_conn, model, 4)  # Fetch the last 4 prompts and responses
    
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
    response_text = response.choices[0].text.strip()
    if response_text:  # This will be False for empty strings
        await ctx.send(response_text)
    else:
        await ctx.send("I'm sorry, I don't have a response for that.")

    # Store the new prompt and response in the 'prompts' table
    await store_prompt(db_conn, username, prompt, model, response_text, channel_name)
    await db_conn.close()
#-----------------------------------------------------------------------
# The '!gpt3' command generates a response using the 'gpt-3.5-turbo' model.
# Similar to the '!davinci3' command, it fetches the last four prompts and responses, and then generates a new response.
@bot.command()
async def gpt3(ctx, *, message):

    model = "gpt-3.5-turbo"
    
    db_conn = await create_connection()
    username = ctx.author.name
    
    channel_name = ctx.channel.name
    
    message_category = await classify_prompt(message)
    
    # await ctx.send(message_category)
    
    if message_category == 'reminder':
        messages = []
        messages.extend([{'role':'user','content':'remind me to turn in my homework next week.'},
                        {'role':'assistant','content':"""{"message":"Turn in homework","reminder_time":"(datetime.now() + timedelta(weeks=1)).strftime('%Y-%m-%d %H:%M:00')"} """}])
        messages.extend([{'role': 'user', 'content': "Remind me in three hours to pick up the kids."},
                      {'role': 'assistant', 'content': """{"message":"Pick up the kids","reminder_time":"(datetime.now() + timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:00')"} """}])
        messages.extend([{'role': 'user', 'content': 'Remind me to buy groceries tomorrow.'},
                        {'role': 'assistant', 'content': """{"message":"Buy groceries","reminder_time":"(datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:00')"} """}])
        messages.extend([{'role': 'user', 'content': 'Remind me in 30 minutes to call my mom.'},
                         {'role': 'assistant', 'content': """{"message":"Call mom","reminder_time":"(datetime.now() + timedelta(minutes=30)).strftime('%Y-%m-%d %H:%M:00')"} """}])
        messages.append({'role':'user','content':f'Put this in the same format as before: {message}'})
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
        
        response_text = eval(response_text)
        
        reminder_time = eval(response_text['reminder_time'])
        
        dictionary = {
            'message': response_text['message'],
            'response_time': reminder_time
        }
        
        await store_prompt(db_conn, ctx.author.name, message, model, f"Reminder set for {reminder_time}.", channel_name)
        
        # Add the new reminder to the database
        await add_reminder(ctx.author.name, response_text['message'], ctx.channel.id, ctx.channel.name, reminder_time)
        
        await ctx.send(f"Reminder set for {reminder_time}.")
        
    elif message_category == 'other':
        past_prompts = await fetch_prompts(db_conn, channel_name, 4)  # Fetch the last 4 prompts and responses

        # Construct the messages parameter with the past prompts and responses and the current message
        messages = []
        # Here we include some examples of reminders for our task model. Ideally, this would be a fine-tuned model,
        # but that requires further setup.
        messages.extend([{'role': 'user', 'content': "Remind me to turn in my homework next week."},
                         {'role': 'assistant', 'content': f'!reminder {(datetime.now() + timedelta(weeks=1)).strftime("%Y-%m-%d")} Turn in homework'}])
        messages.extend([{'role': 'user', 'content': "Remind me in three hours to pick up the kids."},
                         {'role': 'assistant', 'content': f'!reminder {(datetime.now() + timedelta(hours=3)).strftime("%Y-%m-%d %H:%M")} Pick up the kids'}])
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

#-----------------------------------------------------------------------
# '!reminder' command sets a new reminder.
# It takes date, hour, minute, and message as arguments, converts the date and time to a datetime object, 
# and then calls the 'add_reminder' function to add the new reminder to the database.

@bot.command()
async def reminder(ctx, date: str, time: str, *, message: str):
    # Split the time string into hour and minute
    hour, minute = map(int, time.split(':'))

    # Convert the date and time to a datetime object
    reminder_time = datetime.strptime(f"{date} {hour}:{minute}", "%Y-%m-%d %H:%M")

    # If the reminder time is in the past, send an error message
    if reminder_time < datetime.now():
        await ctx.send("Cannot set a reminder for a past time.")
        return

    # Add the new reminder to the database
    await add_reminder(ctx.author.name, message, ctx.channel.id, ctx.channel.name, reminder_time)

    # Send a confirmation message
    await ctx.send(f"Reminder set for {reminder_time.strftime('%Y-%m-%d %H:%M')}.")


#-----------------------------------------------------------------------
# '!label_last' command to correctly label the last prompt.
@bot.command()
async def label_last(ctx,label):
    # Verify the label
    print(label)
    if label not in ['reminder', 'other']:
        await ctx.send("Invalid label. Please use 'reminder' or 'other'.")
        return
    db_conn = await create_connection()
    channel_name = ctx.channel.name
    
    # label_last_prompt
    await label_last_prompt(ctx,db_conn,label)
        

    await ctx.send(f"Last promped labeled as: {label}")

#-----------------------------------------------------------------------
# The 'send_reminders' function is a looping task that runs every minute.
# It fetches all reminders from the 'reminders' table in the SQLite database.
# For each reminder, it checks if the current time is equal to or past the reminder time.
# If it is, the bot sends a message in the appropriate channel mentioning the user and the reminder text.
# After the reminder is sent, it is deleted from the 'reminders' table.
# This function ensures that all reminders are sent at the correct times.

@tasks.loop(minutes=1)
async def send_reminders():
    # Connect to the SQLite3 database named 'data.db'
    conn = await aiosqlite.connect('data.db')
    cursor = await conn.cursor()

    # Select all reminders from the 'reminders' table
    await cursor.execute('SELECT username, reminder, channel_id, channel_name, reminder_time FROM reminders')
    reminders = await cursor.fetchall()

    for reminder in reminders:
        username, reminder_text, channel_id, channel_name, reminder_time = reminder
        # Convert the string reminder_time to a datetime object
        reminder_time = datetime.strptime(reminder_time, "%Y-%m-%d %H:%M:00")

        # Check if the current time is past the reminder time
        if datetime.now() >= reminder_time:
            # If it is, get the user and channel and send the reminder
            channel = bot.get_channel(int(channel_id))
            await channel.send(f"@{username}, you set a reminder: {reminder_text}")

            # Then delete the reminder from the database
            await cursor.execute('DELETE FROM reminders WHERE username = ? AND reminder_time = ?', (username, reminder_time))
            await conn.commit()

    # Close the connection
    await conn.close()

#-----------------------------------------------------------------------
# 'on_ready' function is an event handler that runs after the bot has connected to the server.
# It starts the 'send_reminders' loop.
@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    send_reminders.start()

########################################################################
# Bot Startup Sequence
########################################################################
# This command starts the bot using the DISCORD_BOT_TOKEN environment variable.
# You must replace "DISCORD_BOT_TOKEN" with your actual discord bot token.
bot.run(os.environ.get("DISCORD_BOT_TOKEN"))
