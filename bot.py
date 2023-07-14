import discord
from discord.ext import commands,tasks

from app.config import *


# Set up the bot with '!' as the command prefix. 
# It is set to listen and respond to all types of intents in the server. 
# You can change the command prefix by replacing '!' with your preferred symbol.
bot = commands.Bot(command_prefix="!",intents=discord.Intents.all())

########################################################################
# Bot Boot Sequence
########################################################################
from app.bot_functions import *
from app.keras_layer import *

# Create the prompts table if needed when the bot starts up
asyncio.get_event_loop().run_until_complete(create_prompts_table())
# Create the labeled_prompts table if needed when the bot starts up
asyncio.get_event_loop().run_until_complete(create_labeled_prompts_table())
# Create the reminders table if needed when the bot starts up
asyncio.get_event_loop().run_until_complete(create_reminder_table())
# train the keras layer
asyncio.get_event_loop().run_until_complete(train_keras())
########################################################################
# Bot Commands
########################################################################
from app.fefe import *

@bot.command()
async def fefe(ctx,*,message):
    await talk_to_fefe(ctx,message,bot)
# Used to label the last prompt you sent. 
@bot.command()
async def label_last(ctx,label):
    await label_last_prompt(ctx,label)

# '!clear_reminders` command 
@bot.command()
async def clear_reminders(ctx):
    await clear_user_reminders(ctx)

# '!retrain_keras' command to retrain the model. Must be run by an administrator.
@bot.command()
async def retrain_keras(ctx):
    if ctx.message.author.guild_permissions.administrator:
        await ctx.send('Training. Standby...')
        await train_keras()
        await ctx.send('Training complete.')
    else:
        await ctx.send('Please contact a server admin to update the keras layer')

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
########################################################################
# Bot tasks
########################################################################
@tasks.loop(minutes=1)
async def reminders(bot):
    try:
        await update_reminders_table(bot)
        await send_reminders(bot)

    except Exception as e:
        print(f"Error in send_reminders: {e}")

@tasks.loop(minutes=90)
async def delete_downloads(bot):
    await delete_music_downloads(bot)
    print('Download folder cleared')
    
# 'on_ready' function is an event handler that runs after the bot has connected to the server.
# It starts the 'send_reminders' loop.
@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    reminders.start(bot)
    delete_downloads.start(bot)
bot.run(discord_bot_token)