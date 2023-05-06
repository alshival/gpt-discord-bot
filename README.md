# gpt-discord-bot Starter Code
Discord Bot Starter Code using [openAi](https://openai.com/) by [Alshival's Data Service](https://alshival.com). It is a very basic bot that you can expand on so that you can hit the ground running. It currently implements two models. `text-davinci-002` is cheaper to use than the newer models, hence a great choice for a discord server with many users who are just goofing around, though openAi offers some lighter models that might suffice. `gpt-3.5-turbo model` is heavier and more **$\huge\textcolor{red}{\textsf{great for study groups}}$**  or even **$\huge\textcolor{green}{\textsf{collaboration between small teams.}}$** You can easily swap out the model in the code with anything you need, even fine-tuned models. Check out [openAi's models](https://platform.openai.com/docs/models) for a list of models provided by openAi.


To use `text-davinci-002`, use `!chatGPT`.


<img src="https://github.com/alshival/gpt-discord-bot/blob/main/Screenshot%202023-05-05%204.16.58%20AM.png?raw=true">


To use `gpt-3.5-turbo`, use `!chatGPTturbo`.


<img src="https://github.com/alshival/gpt-discord-bot/blob/main/Screenshot%202023-05-05%2011.50.53%20PM.png?raw=true">

# Installation

So that the bot can respond, it must be running on a machine such as a cloud server, a PC or laptop, or even a raspberry pi in your bedroom (hint for students on a budget).

You'll need a python installation (suggestion for students: get jupyterlab too)

Create a Discord account if you haven't already done so.

Create a new Discord application at the Discord Developer Portal. Once you're logged in, click on the "New Application" button, give your application a name, and click "Create."

Create a bot for your Discord application by clicking on the "Bot" tab and then clicking "Add Bot." Give your bot a name and click "Create."

Generate a token for your bot by clicking on the "Copy" button next to "Token" under the bot's name. Keep this token secure, as it will be used to authenticate your bot with the Discord API.

Install the necessary dependencies. You will need the Discord.py and OpenAI Python modules installed. You can install them using pip by running the following command in your terminal:

```
pip install discord.py openai
```

Set environmental variables `OPENAI_API_KEY`, your actual OpenAI API key, and `DISCORD_BOT_TOKEN`, the token you generated. To do this on Linux, edit your `~/.bashrc` file:

```
export OPENAI_API_KEY = "<API KEY>"
export DISCORD_BOT_TOKEN = "<BOT TOKEN>"
```


Run your bot by executing the following command in your terminal:

```
python gpt_discord_bot.py
```

Your bot should now be up and running! You can invite it to your Discord server by going back to the Discord Developer Portal, selecting your application, clicking on the "OAuth2" tab, selecting the "bot" scope, then select all of the text permissions you need, and copying the generated OAuth2 URL into your browser.
