import discord
from discord.ext import commands
import openai
import os

# Set up the OpenAI API
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Set up the bot
bot = commands.Bot(command_prefix="!",intents=discord.Intents.all())

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
    # Generate a response using GPT
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{'role': 'user', 'content': message}],
        max_tokens=1024,
        n=1,
        temperature=0.5,
        top_p=1,
        frequency_penalty=0.0,
        presence_penalty=0.6,
    )

    # Send the response back to the user
    await ctx.send(response.choices[0]['message']['content'])
    
# Start the bot
bot.run(os.environ.get("DISCORD_BOT_TOKEN"))


