# gpt-discord-bot Starter Code
Discord Bot Starter Code by [Alshival's Data Service](https://alshival.com) using [openAi](https://openai.com/). It is a very basic bot that you can expand on so that you can hit the ground running. It currently implements two models. 

  * `text-davinci-002` is cheaper to use than the heavier models, hence a great choice for a discord server with many users, though openAi offers some lighter models that might meet your needs. 
  * `gpt-3.5-turbo` is heavier and $\huge\textcolor{red}{\textbf{\textsf{great as a tutor for study groups}}}$  or even $\huge\textcolor{green}{\textbf{\textsf{brainstorming with small teams}}}$.
  
Once GPT-4 scales up, we will update the code here to include a `!GPT4` command.
  
  You can easily swap out the model in the code with anything you need, even fine-tuned models. Check out [openAi's models](https://platform.openai.com/docs/models) for a complete list of models. There are $\huge\textcolor{VioletRed}{\textsf{only 7 steps for install}}$.

If you'd like our help building more complicated bots, integrating the bot with your data using a fine-tuned model, or training it to search through documents, visit our website at [Alshival.com](https://alshival.com).

Note that data privacy laws may come into play, such as Q&A bots for legal or medical documents. For these, a self-hosted solution rather than discord would be required.

The basic bot doesn't remember conversations. Note further that `!chatGPTturbo` may take a few seconds to run.

### **Update 2023-05-15: `gpt_discord_bot_v2.py`** 
`gpt_discord_bot_v2.py` is our good ol' `gpt_discord_bot.py`, but with a SQLite3 database for memory storage. This bot DOES remember. The database stores 200 interactions though can be customized. The bot is set up to remember the past 4 interactions with the bot from which `!chatGPT` and `!chatGPTturbo` are called, independent of who submitted the prompt and what model they used. This can be adjusted in the code.  

Discord has a 2,000 character limit, so that is your input limit. Note that this does not check for token limits, as the tiktokens package was not working properly on my chromebook as the package requires an older version of python. Including historical messages could lead you to hitting against this limit.

<p align="center">
<img src="https://github.com/alshival/gpt-discord-bot/blob/main/.meta/gpt-discord-bot-v2%20(2).png?raw=true" width="75%" height="75%">
</p>

# Usage
To use `text-davinci-002` in Discord, type `!chatGPT` before your request.


<img src="https://github.com/alshival/gpt-discord-bot/blob/main/.meta/Screenshot%202023-05-05%204.16.58%20AM.png?raw=true">

To use `gpt-3.5-turbo` in Discord, type `!chatGPTturbo` before your request.

<img src="https://github.com/alshival/gpt-discord-bot/blob/main/.meta/Screenshot%202023-05-05%2011.50.53%20PM.png?raw=true">
P.S... Salski and I prefer using USB ports or RJ-45... but. You know... To each, their own.


A data science student approached me on UpWork to help with their homework. I helped them with the graph theory problems then told them just chug the rest through GPT. They were probability and calculus problems that I knew GPT could handle.  Advised them to form a study group and gave them a link to this bot. It works great for tutoring. Plus it would be cheaper for them to just ask GPT.

If you want to learn Ai, then you can use Ai to help you learn Ai. As a mathematician, I was surprised by how capable these models are. I verified a few results and felt comfortable enough to recommend it to them.

<img src="https://github.com/alshival/gpt-discord-bot/blob/main/.meta/Screenshot%202023-05-12%202.37.22%20AM.png?raw=true">


# Installation

So that the bot can respond, it must be running on a machine such as a cloud server, a PC or laptop, or even a raspberry pi in your bedroom (hint for students on a budget).

You'll need a python installation (suggestion for students: get jupyterlab too) and an [openAi API key](https://platform.openai.com/account/api-keys).

### Step 1
Create a Discord account if you haven't already done so.

### Step 2
Create a new Discord application at the [Discord Developer Portal](https://discord.com/login?redirect_to=%2Fdevelopers%2Fapplications). Once you're logged in, click on the "New Application" button, give your application a name, and click "Create."

### Step 3
Create a bot for your Discord application by clicking on the "Bot" tab and then clicking "Add Bot." Give your bot a name and click "Create."

### Step 4
Generate a token for your bot by clicking on the "Copy" button next to "Token" under the bot's name. Keep this token secure, as it will be used to authenticate your bot with the Discord API.

### Step 5
Install the necessary dependencies. You will need the Discord.py and OpenAI Python modules installed. You can install them using pip by running the following command in your terminal:

```
pip install discord.py openai
```

### Step 6
Set environmental variables `OPENAI_API_KEY`, your actual OpenAI API key, and `DISCORD_BOT_TOKEN`, the token you generated. To do this on Linux, edit your `~/.bashrc` file:

```
export OPENAI_API_KEY = "<API KEY>"
export DISCORD_BOT_TOKEN = "<BOT TOKEN>"
```
Replace <API KEY> with your openAi API key and <BOT TOKEN> with the token you created in Step 4.

You can edit your `~/.bashrc` file using a command line text editor like **nano** on a raspberry pi. 
```
nano ~/.bashrc
```
Make changes and hit Ctrl+X to save and close.

### Step 7
Run your bot by executing the following command in your terminal:

```
python gpt_discord_bot.py
```

Your bot should now be up and running! You can invite it to your Discord server by going back to the Discord Developer Portal, selecting your application, clicking on the "OAuth2" tab, selecting the "bot" scope, then select all of the text permissions you need, and copying the generated OAuth2 URL into your browser.
