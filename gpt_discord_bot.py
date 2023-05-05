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
async def chatGPT(ctx, *, prompt):
    # Generate a response using GPT
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.7,
    )

    # Send the response back to the user
    await ctx.send(response.choices[0].text)

# Start the bot
bot.run(os.environ.get("DISCORD_BOT_TOKEN"))
