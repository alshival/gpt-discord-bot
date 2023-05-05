import discord
import openai
import os


# Set up the OpenAI API
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Set up the Discord client
client = discord.Client()

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Generate a response using GPT
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=message.content,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.7,
    )

    # Send the response back to the user
    await message.channel.send(response.choices[0].text)

# Start the bot
client.run("DISCORD_BOT_TOKEN")
