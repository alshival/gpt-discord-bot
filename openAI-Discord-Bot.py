########################################################################
# This script creates a Discord bot that interacts with users using 
# OpenAI's GPT models. It keeps a history of its past conversations,
# allowing it to generate responses based on previous interactions. 
# This script should be customized as per the user's requirements.
# It utilizes the OpenAI API and SQLite3 database to store and retrieve 
# past conversations. 
########################################################################
import os
import openai
import discord

# Set up Discord Bot token here:
discord_bot_token = os.environ.get("DISCORD_BOT_TOKEN")
# Set up the OpenAI API. The key is stored as an environment variable for security reasons. 
openai.api_key = os.environ.get("OPENAI_API_KEY")
# Set up the Google Youtube Data API key
google_api_key = os.environ.get("google_api_key")

# Define setup variables here
db_name = 'data.db'
epochs = 25 # Number of training epochs. 
prompt_table_cache_size = 200 # Number of prompts stored in the local SQLite database. The table is truncated when the bot starts up.

keras_labels = ['other','reminder','youtube']
# other - pure openAi model.
# reminder - set a reminder task.
# youtube - search youtube.
# social - socializing.

########################################################################

from discord.ext import commands,tasks
from datetime import datetime, timedelta
import sqlite3
import aiosqlite
import asyncio
import json
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import youtube_dl
import yt_dlp

# Set up the bot with '!' as the command prefix. 
# It is set to listen and respond to all types of intents in the server. 
# You can change the command prefix by replacing '!' with your preferred symbol.
bot = commands.Bot(command_prefix="!",intents=discord.Intents.all())


########################################################################
# Database Prep
########################################################################
# Delete files in the `downloads` directory
for file_name in os.listdir('downloads'):
    file_path = os.path.join('downloads',file_name)
    if os.path.isfile(file_path):
        os.remove(file_path)
    elif os.path.isdir(file_path):
        empty_directory(file_path)
        os.rmdir(file_path)

# This function establishes a global connection to the 'data.db' SQLite database.
# It is used by some other functions whenever they need to interact with the database.
async def create_connection():
    return await aiosqlite.connect(db_name)

#-----------------------------------------------------------------------
# This function is used to retrieve a list of channels. 
# Originally created to aid in the removal of reminders from channels
# that no longer exist in the `reminders` table within `data.db`.
async def list_channels(bot):
    channel_names = []
    for guild in bot.guilds:
        for channel in guild.channels:
            # if isinstance(channel, discord.TextChannel): # If you want text channels only
            #     channel_names.append(channel.name)
            channel_names.append(channel.name)
    return channel_names
#-----------------------------------------------------------------------
# This function creates a table named 'prompts' in the SQLite database 'data.db' upon bot startup.
# The table is used to store the bot's conversation history.
# The table has fields for id, username, prompt, model, response, channel_name, and timestamp.
async def create_prompts_table():
    # Connect to the SQLite3 database named 'data.db'
    conn = await aiosqlite.connect(db_name)
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
                  keras_classified_as TEXT,
                  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

    # Commit the changes and close the connection
    await conn.commit()
    await conn.close()
    
# The 'create_table' function is called using the asyncio event loop when the bot starts up.
asyncio.get_event_loop().run_until_complete(create_prompts_table())

#-----------------------------------------------------------------------
# This function is used to store a new conversation in the 'prompts' table.
# It inserts a new row with the username, prompt, model, response, and channel_name into the table.
async def store_prompt(db_conn, username, prompt, model, response, channel_name,keras_classified_as):
    async with db_conn.cursor() as cursor:
        await cursor.execute('INSERT INTO prompts (username, prompt, model, response, channel_name,keras_classified_as) VALUES (?, ?, ?, ?, ?, ?)', (username, prompt, model, response, channel_name,keras_classified_as))
        await db_conn.commit()

#-----------------------------------------------------------------------
# 'create_labeled_prompts_table' function creates a new table named 'labeled_prompts' in the SQLite database 'data.db'.
# This table is used to quickly label the last channel prompt as a 'reminder' request or 'order' request. 
# Use `!label_last reminder` or `!label_last other` in Discord.

async def create_labeled_prompts_table():
    conn = await aiosqlite.connect(db_name)
    cursor = await conn.cursor()
    await cursor.execute('''CREATE TABLE IF NOT EXISTS labeled_prompts
                      (id INTEGER PRIMARY_KEY,
                      username TEXT NOT NULL,
                      prompt TEXT NOT NULL,
                      model TEXT,
                      response TEXT,
                      channel_id TEXT,
                      channel_name TEXT,
                      keras_classified_as,
                      timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      label TEXT)''')
    await conn.commit()
    await conn.close()

asyncio.get_event_loop().run_until_complete(create_labeled_prompts_table())
#----------------------------------------------------------------------
# Used by users to label past prompts. 

async def label_last_prompt(ctx,db_conn, label):
    db_conn.row_factory = sqlite3.Row
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
            last_row = dict(last_row)
            insert_query = '''INSERT INTO labeled_prompts (id, username, prompt, model, response, channel_id, channel_name,keras_classified_as,timestamp,label)
                              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
            
            await cursor.execute(insert_query,
                                 tuple([last_row[key] for key in last_row.keys()] + [label]))
            await db_conn.commit()
            await ctx.send(f"Last prompt labeled as: {label} - {last_row['prompt']}")


#-----------------------------------------------------------------------
# This function is used to fetch past conversations from the 'prompts' table.
# It fetches a set number of past prompts and responses from a specific channel.
# The 'limit' parameter determines how many past conversations to fetch.
async def fetch_prompts(db_conn, channel_name, limit):
    async with db_conn.cursor() as cursor:
        await cursor.execute('SELECT prompt, response FROM prompts WHERE channel_name = ? ORDER BY timestamp DESC LIMIT ?', (channel_name, limit,))
        return await cursor.fetchall()

#-----------------------------------------------------------------------
# '!label_last' command to correctly label the last prompt.
@bot.command()
async def label_last(ctx,label):
    # Verify the label
    
    if label not in keras_labels:
        await ctx.send("Invalid label. Please use `!label_last reminder` if you meant to set a reminder, '!label_last youtube' for youtube, or `!label_last other` for the raw openAi model.")
        return
    db_conn = await create_connection()
    channel_name = ctx.channel.name
    
    # label_last_prompt
    await label_last_prompt(ctx,db_conn,label)

########################################################################
# Reminders Prep
########################################################################
#-----------------------------------------------------------------------
# 'create_reminder_table' function creates a new table named 'reminders' in the SQLite database 'data.db'.
# This table is used to store reminders set by users.
# The table has fields for id, username, message, channel_name, and reminder_time.
async def create_reminder_table():
    conn = await aiosqlite.connect(db_name)
    cursor = await conn.cursor()

    await cursor.execute('''CREATE TABLE IF NOT EXISTS reminders
                  (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT NOT NULL,
                  reminder TEXT NOT NULL,
                  channel_id TEXT NOT NULL,
                  channel_name TEXT NOT NULL,
                  reminder_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    # Delete reminders that build up each time the bot boots.
    # Clear out rows with null reminder_time
    await cursor.execute("DELETE FROM reminders WHERE reminder_time IS NULL")
    await conn.commit()
    await conn.close()

asyncio.get_event_loop().run_until_complete(create_reminder_table())
#-----------------------------------------------------------------------
# 'add_reminder' function is used to add a new reminder to the 'reminders' table.
# It takes username, message, channel_name, and reminder_time as arguments and inserts a new row into the table.

async def add_reminder(username, reminder, channel_id, channel_name, reminder_time):
    conn = await aiosqlite.connect(db_name)
    cursor = await conn.cursor()

    await cursor.execute('INSERT INTO reminders (username, reminder, channel_id, channel_name, reminder_time) VALUES (?, ?, ?, ?, ?)',
                         (username, reminder, channel_id, channel_name, reminder_time))
    await conn.commit()
    await conn.close()
#-----------------------------------------------------------------------
# 'delete_reminder' function deletes a reminder from the 'reminders' table.
# It takes the id of the reminder to be deleted as an argument.

async def delete_reminder(reminder_id):
    conn = await aiosqlite.connect(db_name)
    cursor = await conn.cursor()

    await cursor.execute('DELETE FROM reminders WHERE id = ?', (reminder_id,))
    await conn.commit()
    await conn.close()
#-----------------------------------------------------------------------
# 'fetch_due_reminders' function fetches all reminders that are due to be sent.
# It selects all reminders from the 'reminders' table where the reminder_time is less than or equal to the current timestamp.

async def fetch_due_reminders():
    conn = await aiosqlite.connect(db_name)
    cursor = await conn.cursor()

    await cursor.execute('SELECT id, username, reminder, channel_id, channel_name FROM reminders WHERE reminder_time <= CURRENT_TIMESTAMP')
    reminders = await cursor.fetchall()

    await conn.close()

    return reminders
#-----------------------------------------------------------------------
# '!clear_reminders` command 
@bot.command()
async def clear_reminders(ctx):
    """Clears all reminders of the invoking user"""
    conn = await aiosqlite.connect(db_name)
    cursor = await conn.cursor()

    # Delete records from the reminders table where username is ctx.author.name
    await cursor.execute("DELETE FROM reminders WHERE username=?", (str(ctx.author.name),))
    await conn.commit()
    await conn.close()

    await ctx.send('All your reminders have been cleared.')

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

########################################################################
# youtube
########################################################################
# Set up the YouTube Data API client
youtube = build("youtube", "v3", developerKey=google_api_key)

@bot.command()
async def search_youtube(ctx, *, query):
    try:
        # Call the search.list method to search for videos
        search_response = youtube.search().list(
            q=query,
            part="id,snippet",
            maxResults=3
        ).execute()

        # Create a formatted string with the video titles
        video_titles = "\n".join(
            f"""[{search_result["snippet"]["title"]}](https://www.youtube.com/watch?v={search_result["id"]["videoId"]})"""
            for search_result in search_response.get("items", [])
            if search_result["id"]["kind"] == "youtube#video"
        )

        # Send the video titles as a message in the Discord channel
        await ctx.send(f"Search results for '{query}':\n{video_titles}")

    except HttpError as e:
        await ctx.send("An HTTP error occurred.")
        print("An HTTP error occurred:")
        print(e)

#These are options for the youtube dl, not needed actually but are recommended
ytdlopts = { 
    'format': 'bestaudio/best',
    'outtmpl': 'downloads/%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',  
    'force-ipv4': True,
    'preferredcodec': 'mp3',
    'cachedir': False
    
    }

ffmpeg_options = {
        'options': '-vn'
    }

ytdl = yt_dlp.YoutubeDL(ytdlopts)

@bot.command()
async def play(ctx, *, query):
    try:
        voice_channel = ctx.author.voice.channel #checking if user is in a voice channel
    except AttributeError:
        return await ctx.send("No channel to join. Make sure you are in a voice channel.") #member is not in a voice channel

    permissions = voice_channel.permissions_for(ctx.me)
    if not permissions.connect or not permissions.speak:
        await ctx.send("I don't have permission to join or speak in that voice channel.")
        return
    
    voice_client = ctx.guild.voice_client
    if not voice_client:
        await voice_channel.connect()
        voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)

    loop = asyncio.get_event_loop()
    data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url=query, download=True)) #extracting the info and not downloading the source

    
    title = data['title'] #getting the title
    song = data['url'] #getting the url

    if 'entries' in data: #checking if the url is a playlist or not
            data = data['entries'][0] #if its a playlist, we get the first item of it

    try:
        voice_client.play(discord.FFmpegPCMAudio(source=song,**ffmpeg_options, executable="ffmpeg")) #playing the audio
    except Exception as e:
        print(e)

    await ctx.send(f'**Now playing:** {title}') #sending the title of the video

########################################################################
# Bot Prep
########################################################################
#-----------------------------------------------------------------------
# This function ensures the bot's memory usage remains low by maintaining a maximum of prompt_table_cache_size responses in the database.
# It deletes the oldest entries if the count exceeds prompt_table_cache_size.
# This function is also called upon bot startup.
# You can customize the maximum number of entries by changing the 'max_rows' variable.
async def update_cache():
    # Connect to the SQLite3 database named 'data.db'
    conn = await create_connection()
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

########################################################################
# Keras Task Assigner
########################################################################
# This code demonstrates a simple task assigner using Keras, which classifies
# messages as either 'reminder' or 'other'. It is used before GPT in order
# to classify which type of task will be run.
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Embedding, GlobalMaxPooling1D
from tensorflow.keras.optimizers import Adam

max_sequence_length = None
word_to_index = None
model = None
label_to_index = None 

async def train_keras():
    global max_sequence_length
    global word_to_index
    global label_to_index
    global model

    # Dummy training data generated using GPT4
    messages = [
        """
        Introducing your new digital bestie, our latest and greatest Discord bot! Not only can it masterfully converse with the proficiency of OpenAI's GPT models, but it's also got a knack for organizing your life. Tell it in your own words to remind you of anything - from picking up groceries to calling your mom - and it will remember, no fancy commands needed! But that's not all - ever feel like a quick game of tic-tac-toe? Challenge our bot and enjoy a fun, engaging game right in your chat. 
        Whether you're up for a chat, need a little help staying on top of things, or just want to have some fun, this bot has got you covered!
        """,
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
        "In a short answer, tell me how to write pi/2 as an infinite sum.",
        "Play Spirit in the Sky.",
        "I want to listen to Jay-Z",
        "Can you find a video explaining how quantum computers work?",
        "Play the phantom of the opera.",
        "play a song from the guardians of the galaxy soundtrack.",
        "can you find a video about the mathematics of neural networks?",
    ]
    labels = [
        'other','reminder','reminder','other','reminder','other',
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
        'other','other','youtube','youtube','youtube','youtube','youtube','youtube',
    ]
    #---------------------------------------------
    # Check if `data.db` has labeled_prompts table
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    # Execute the query to retrieve the table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    tables = [table[0] for table in tables]
    if 'labeled_prompts' in tables:
        cursor.execute("select prompt,label from labeled_prompts")
        rows = cursor.fetchall()
        if rows is not None:
            dict_rows = [dict(row) for row in rows]
            messages += [row['prompt'] for row in dict_rows]
            labels += [row['label'] for row in dict_rows]
        
    conn.close()
    
    #---------------------------------------------
    # Preprocessing
    vocab = set(' '.join(messages).lower().split())
    vocab_size = len(vocab)
    word_to_index = {word: index for index, word in enumerate(vocab)}
    max_sequence_length = max(len(message.split()) for message in messages)
    #---------------------------------------------
    # Convert sentences to numerical sequences
    X = np.zeros((len(messages), max_sequence_length))
    for i, message in enumerate(messages):
        words = message.lower().split()
        for j, word in enumerate(words):
            X[i, j] = word_to_index[word]
      #---------------------------------------------
    # Convert labels to numerical values
    label_to_index = dict(zip(keras_labels,range(len(keras_labels))))#{'reminder': 0, 'other': 1, 'youtube': 2}
    y = np.array([label_to_index[label] for label in labels])

    # Define the model
    model = Sequential()
    model.add(Embedding(input_dim=vocab_size, output_dim=50, input_length=max_sequence_length))
    model.add(GlobalMaxPooling1D())
    model.add(Dense(16, activation='relu'))
    model.add(Dense(len(keras_labels), activation='softmax'))  # assuming you have 3 classes

    # Compile the model
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy']) 


    # Train the model
    model.fit(X, y, epochs=epochs, batch_size=1, verbose=1)

# Train the model when the bot starts up.
asyncio.get_event_loop().run_until_complete(train_keras())

#-----------------------------------------------------------------------
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
    predicted_index = np.argmax(prediction)  # Change here, get the index of max value
    index_to_label = {v: k for k, v in label_to_index.items()}
    predicted_label = index_to_label[predicted_index]

    return predicted_label


#-----------------------------------------------------------------------
# '!retrain_keras' command to retrain the model. Must be run by an administrator.
@bot.command()
async def retrain_keras(ctx):
    if ctx.message.author.guild_permissions.administrator:
        await ctx.send('Training. Standby...')
        await train_keras()
        await ctx.send('Training complete.')
    else:
        await ctx.send('Please contact a server admin to update the keras layer')

#-----------------------------------------------------------------------
# Used to abide by Discord's 2000 character limit.
async def send_chunks(ctx, text):
    chunk_size = 2000  # Maximum length of each chunk

    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

    for chunk in chunks:
        await ctx.send(chunk)
#-----------------------------------------------------------------------
# The '!davinci3' command generates a response using the 'text-davinci-002' model.
@bot.command()
async def davinci(ctx, *, prompt):
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
        if len(response_text) > 2000:
            await send_chunks(ctx, response_text)
        else:
            await ctx.send(response_text)
    else:
        await ctx.send("I'm sorry, I don't have a response for that.")


    # Store the new prompt and response in the 'prompts' table
    await store_prompt(db_conn, username, prompt, model, response_text, channel_name,keras_classified_as = None)
    await db_conn.close()

#-----------------------------------------------------------------------
# The '!gpt3' command generates a response using the 'text-davinci-002' model.
# It fetches the last four prompts and responses from the database, and then generates a new response.
@bot.command()
async def fefe(ctx, *, message):

    model = "gpt-3.5-turbo"
    
    db_conn = await create_connection()
    username = ctx.author.name
    
    channel_name = ctx.channel.name
    try:
        message_category = await classify_prompt(message)
        message_classified =True
    except Exception as e:
        # Capture the error message
        error_message = str(e)
        print(type(message))
        print(message)
        await ctx.send("""
        I'll need a bit more training to answer your question.
        Can you run `!label_last <label>` by replacing '<label>' with one of the following?
        
            * `reminder` - for reminder requests.
            * `other` - for everything else.
            
        After that, run `!retrain_keras`, wait for me to think a bit, and then ask me again.
        """)
        await store_prompt(db_conn, ctx.author.name, message, model,'', channel_name,keras_classified_as = 'ERROR')
        return

    # bot's Reminder Capabilities
    if message_category == 'reminder':
        messages = []
        messages.extend([{'role':'user','content':'remind me to turn in my homework next week in the morning.'},
                        {'role':'assistant','content':"""{"message":"Turn in homework","reminder_time":"(datetime.now() + timedelta(weeks=1)).strftime('%Y-%m-%d 09:00:00')"} """}])
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
        try:
            response_text = eval(response_text)

            reminder_time = eval(response_text['reminder_time'])
        except Exception as e:
            await ctx.send(response_text)
        
        dictionary = {
            'message': response_text['message'],
            'response_time': reminder_time
        }
        
        await store_prompt(db_conn, ctx.author.name, message, model, f"Reminder set for {reminder_time}.", channel_name,keras_classified_as='reminder')
        
        # Add the new reminder to the database
        await add_reminder(ctx.author.name, response_text['message'], ctx.channel.id, ctx.channel.name, reminder_time)
        await ctx.send(f"Reminder set for {reminder_time}.")
    
    # Bot's openAi capabilities
    elif message_category == 'other':
        past_prompts = await fetch_prompts(db_conn, channel_name, 5)  # Fetch the last 5 prompts and responses
        messages = []
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
        if len(response_text) > 2000:
            await send_chunks(ctx, response_text)
        else:
            await ctx.send(response_text)

        # Store the new prompt and response in the 'prompts' table
        await store_prompt(db_conn, username, message, model, response_text, channel_name,keras_classified_as='other')
        await db_conn.close()
    
    # Bot's youtube capabilities
    elif message_category == 'youtube':
        try:
            voice_channel = ctx.author.voice.channel #checking if user is in a voice channel
        except AttributeError:
            await store_prompt(db_conn, username, message, model, '', channel_name,keras_classified_as='youtube')
            return await ctx.send("No channel to join. Make sure you are in a voice channel.") #member is not in a voice channel
            
        permissions = voice_channel.permissions_for(ctx.me)
        if not permissions.connect or not permissions.speak:
            await store_prompt(db_conn, username, message, model, '', channel_name,keras_classified_as='youtube')
            await ctx.send("I don't have permission to join or speak in that voice channel.")
            return
            
        messages = [{'role':'user','content':'Return a youtube search query based on the following message: Play spirit in the sky'},
                   {'role':'assistant','content':'Spirit in the Sky'},
                   {'role':'user','content':'Return a youtube search query based on the following message: Play the Lion King song'},
                   {'role':'assistant','content':"I just can't wait to be king"},
                   {'role':'user','content':'Return a youtube search query based on the following message: ' +message}]
        response = openai.ChatCompletion.create(
            model=model,
            messages = messages,
            max_tokens=1024,
            n=1,
            temperature=0.5,
            top_p=1
        )
        response_text = response['choices'][0]['message']['content']
        
        try:
            # Call the search.list method to search for videos
            search_response = youtube.search().list(
                q=response_text,
                part="id,snippet",
                maxResults=1
            ).execute()
            search_result = [x for x in search_response.get("items",[]) if x["id"]["kind"] == "youtube#video"][0]
            
            video_url = f"""https://youtu.be/{search_result["id"]["videoId"]}"""
            video_title = f"""### {search_result["snippet"]["title"]}"""
            
        except HttpError as e:
            await ctx.send("An HTTP error occurred.")
            print("An HTTP error occurred:")
            print(e)
            
        voice_client = ctx.guild.voice_client
        if not voice_client:
            await voice_channel.connect()
            voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url=video_url, download=True)) #extracting the info and not downloading the source
            
        title = data['title'] #getting the title
        song = data['url'] #getting the url
        
        if 'entries' in data: #checking if the url is a playlist or not
            data = data['entries'][0] #if its a playlist, we get the first item of it
        try:
            voice_client.play(discord.FFmpegPCMAudio(source=song,**ffmpeg_options, executable="ffmpeg")) #playing the audio
        except Exception as e:
            print(e)
        
        await ctx.send(f"### Playing: {title}\n{video_url}")

            # Store the new prompt and response in the 'prompts' table
        await store_prompt(db_conn, username, message, model, response_text, channel_name,keras_classified_as='youtube')

# this command stops the bot from playing music
@bot.command()
async def stop_music(ctx):
    voice_state = ctx.author.voice
    if voice_state is None or voice_state.channel is None:
        await ctx.send("You are not connected to a voice channel.")
        return

    voice_channel = voice_state.channel
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)

    if voice_client and voice_client.is_connected() and voice_client.channel == voice_channel:
        await voice_client.disconnect()
        await ctx.send("Music playback stopped.")
    else:
        await ctx.send("The bot is not currently playing any music.")

#-----------------------------------------------------------------------
# Start sending reminders, every minute.
@tasks.loop(minutes=1)
async def send_reminders(bot):
    try:
        # This code should be replaced with something that can handle multiple guilds,
        # but for now, we will just use one guild.
        current_channels = await list_channels(bot)
        
        async with aiosqlite.connect(db_name) as conn:
            cursor = await conn.cursor()

            # Clear out rows with null reminder_time
            await cursor.execute("DELETE FROM reminders WHERE reminder_time IS NULL")

            # # Clear out reminders from deleted channels.
            # await cursor.execute("SELECT distinct channel_name FROM reminders")
            # channels_in_table = [row[0] for row in await cursor.fetchall()]

            # # Find the channels that exist in the table but are not present in the current channels
            # channels_to_delete = set(channels_in_table) - set(current_channels)

            # # Delete the channels from the SQLite table
            # for channel in channels_to_delete:
            #     await cursor.execute("DELETE FROM reminders WHERE channel_name = ?", (channel,))

            # Send out the reminders
            await cursor.execute('SELECT username, reminder, channel_id, channel_name, reminder_time FROM reminders WHERE reminder_time is not null')
            reminders = await cursor.fetchall()

            for reminder in reminders:
                username, reminder_text, channel_id, channel_name, reminder_time = reminder
                reminder_time = datetime.strptime(reminder_time, "%Y-%m-%d %H:%M:%S")

                if datetime.now() >= reminder_time:
                    channel = bot.get_channel(int(channel_id))
                    if channel is not None:
                        await channel.send(f"@{username}, you set a reminder: {reminder_text}")
                    else:
                        print(f"Channel with ID {channel_id} not found.")

                    await cursor.execute('DELETE FROM reminders WHERE username = ? AND reminder_time = ?',
                                         (username, reminder_time.strftime("%Y-%m-%d %H:%M:%S"),))

            # Commit the changes here
            await conn.commit()

    except Exception as e:
        print(f"Error in send_reminders: {e}")

# 'on_ready' function is an event handler that runs after the bot has connected to the server.
# It starts the 'send_reminders' loop.
@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    send_reminders.start(bot)

  
########################################################################
# Bot Startup Sequence
########################################################################
# This command starts the bot using the DISCORD_BOT_TOKEN environment variable.
# You must replace "DISCORD_BOT_TOKEN" with your actual discord bot token.
bot.run(discord_bot_token)

        