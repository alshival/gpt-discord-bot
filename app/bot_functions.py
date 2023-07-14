from app.config import *

#############################################
# `prompts` Table
#############################################
# This function creates the prompts table. It is always run when the bot boots up.
async def create_prompts_table():
    # Connect to the SQLite3 database named 'data.db'
    conn = await create_connection()
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
    
# This function is used to store a new conversation in the 'prompts' table.
# It inserts a new row with the username, prompt, model, response, and channel_name into the table.
async def store_prompt(db_conn, username, prompt, model, response, channel_name,keras_classified_as):
    async with db_conn.cursor() as cursor:
        await cursor.execute('INSERT INTO prompts (username, prompt, model, response, channel_name,keras_classified_as) VALUES (?, ?, ?, ?, ?, ?)', (username, prompt, model, response, channel_name,keras_classified_as))
        await db_conn.commit()

# This function is used to fetch past conversations from the 'prompts' table.
async def fetch_prompts(db_conn, channel_name, limit):
    async with db_conn.cursor() as cursor:
        await cursor.execute('SELECT prompt, response FROM prompts WHERE channel_name = ? ORDER BY timestamp DESC LIMIT ?', (channel_name, limit,))
        return await cursor.fetchall()
        
#############################################
# `labeled_prompts` Table
#############################################

async def create_labeled_prompts_table():
    conn = await create_connection()
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


# Used by users to label past prompts. 
async def label_last_db(ctx,db_conn, label):
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

# '!label_last' command to correctly label the last prompt.
async def label_last_prompt(ctx,label):
    # Verify the label
    if label not in keras_labels:
        await ctx.send("Invalid label. Please use `!label_last reminder` if you meant to set a reminder, '!label_last youtube' for youtube, or `!label_last other` for the raw openAi model.")
        return
    db_conn = await create_connection()
    channel_name = ctx.channel.name
    
    # label_last_prompt
    await label_last_db(ctx,db_conn,label)

#############################################
# `Reminders` Table
#############################################

async def create_reminder_table():
    conn = await create_connection()
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
    
# 'add_reminder' function is used to add a new reminder to the 'reminders' table.
async def add_reminder(username, reminder, channel_id, channel_name, reminder_time):
    conn = await aiosqlite.connect(db_name)
    cursor = await conn.cursor()

    await cursor.execute('INSERT INTO reminders (username, reminder, channel_id, channel_name, reminder_time) VALUES (?, ?, ?, ?, ?)',
                         (username, reminder, channel_id, channel_name, reminder_time))
    await conn.commit()
    await conn.close()

# 'delete_reminder' function deletes a reminder from the 'reminders' table using the reminder_id.
async def delete_reminder(reminder_id):
    conn = await aiosqlite.connect(db_name)
    cursor = await conn.cursor()

    await cursor.execute('DELETE FROM reminders WHERE id = ?', (reminder_id,))
    await conn.commit()
    await conn.close()
    
# 'fetch_due_reminders' function fetches all reminders that are due to be sent.
# It selects all reminders from the 'reminders' table where the reminder_time is less than or equal to the current timestamp.
async def fetch_due_reminders():
    conn = await aiosqlite.connect(db_name)
    cursor = await conn.cursor()

    await cursor.execute('SELECT id, username, reminder, channel_id, channel_name FROM reminders WHERE reminder_time <= CURRENT_TIMESTAMP')
    reminders = await cursor.fetchall()

    await conn.close()

    return reminders

async def clear_user_reminders(ctx):
    """Clears all reminders of the invoking user"""
    conn = await aiosqlite.connect(db_name)
    cursor = await conn.cursor()
    # Delete records from the reminders table where username is ctx.author.name
    await cursor.execute("DELETE FROM reminders WHERE username=?", (str(ctx.author.name),))
    await conn.commit()
    await conn.close()

    await ctx.send('All your reminders have been cleared.')

#############################################
# Routine Maintenance Functions
#############################################
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

# This function ensures the bot's memory usage remains low by maintaining a maximum of prompt_table_cache_size responses in the database.
# It deletes the oldest entries if the count exceeds prompt_table_cache_size.
# This function is also called upon bot startup.
# You can customize the maximum number of entries by changing the 'max_rows' variable.
async def delete_music_downloads(bot):
    # Delete music downloads.
    directory = 'app/downloads'
    if os.path.exists(directory) and os.path.isdir(directory):
        for file_name in os.listdir(directory):
            file_path = os.path.join(directory, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                empty_directory(file_path)
                os.rmdir(file_path)

async def update_reminders_table(bot):
    # Connect to the SQLite3 database named 'data.db'
    conn = await create_connection()
    cursor = await conn.cursor()
    # Delete reminders with null value:
    await cursor.execute("DELETE FROM reminders WHERE reminder_time IS NULL")
    await conn.commit()
    # Remove stale data. Currently, the last 200 record are kept.
    # To change this, edit `prompt_table_cache_size` in `app/config.py`
    await cursor.execute('SELECT COUNT(*) FROM prompts')
    count = (await cursor.fetchall())[0][0]
    max_rows = prompt_table_cache_size 
    if count >= max_rows:
        delete_count = count - max_rows - 1  # Calculate how many entries to delete
        await cursor.execute(f'DELETE FROM prompts WHERE id IN (SELECT id FROM prompts ORDER BY timestamp ASC LIMIT {delete_count})')
        await conn.commit()  # Commit the changes
    # Close the database connection
    await conn.close()

    current_channels = await list_channels(bot)
    async with aiosqlite.connect(db_name) as conn:
            cursor = await conn.cursor()
    
    # Delete reminders from channels that no longer exist
    current_channels = await list_channels(bot)

async def send_reminders(bot):
    conn = await create_connection()
    cursor = await conn.cursor()
    # Send out the reminders
    await cursor.execute('''
    SELECT 
        username, 
        reminder, 
        channel_id, 
        channel_name, 
        reminder_time 
    FROM reminders 
    WHERE reminder_time is not null''')
    
    reminders = await cursor.fetchall()
    
    for reminder in reminders: 
        username, reminder_text, channel_id, channel_name, reminder_time = reminder
        reminder_time = datetime.strptime(reminder_time,"%Y-%m-%d %H:%M:%S")
        
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