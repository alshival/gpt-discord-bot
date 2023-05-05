# gpt-discord-bot
Discord Bot by Alshival's Data Service. Visit [Alshival.com](Alshival.com).

Integrating GPT with Discord can be done by creating a Discord bot that utilizes the GPT API to generate text responses to user input. Here's a step-by-step guide to get you started:

Create a Discord account if you haven't already done so.

Create a new Discord application at the Discord Developer Portal. Once you're logged in, click on the "New Application" button, give your application a name, and click "Create."

Create a bot for your Discord application by clicking on the "Bot" tab and then clicking "Add Bot." Give your bot a name and click "Create."

Generate a token for your bot by clicking on the "Copy" button next to "Token" under the bot's name. Keep this token secure, as it will be used to authenticate your bot with the Discord API.

Install the necessary dependencies. You will need the Discord.py and OpenAI Python modules installed. You can install them using pip by running the following command in your terminal:

```
pip install discord.py openai
```

Create a Python script that will serve as your bot. Here's an example script that uses GPT to generate responses to user input.

Set environmental variables `OPENAI_API_KEY`, your actual OpenAI API key, and `DISCORD_BOT_TOKEN`, the token you generated in step 4. To do this on Linux, edit your `~/.bashrc` file:

```
export OPENAI_API_KEY = "<API KEY>"
export DISCORD_BOT_TOKEN = "<BOT TOKEN>"
```


Run your bot by executing the following command in your terminal:

```
python gpt_discord_bot.py
```

Your bot should now be up and running! You can invite it to your Discord server by going back to the Discord Developer Portal, selecting your application, clicking on the "OAuth2" tab, selecting the "bot" scope, then select all of the text permissions you need, and copying the generated OAuth2 URL into your browser.

The bot is called using `!chatGPT`.

```
!chatGPT Say hi to the Github community!
```
`Hello, Github community!`

