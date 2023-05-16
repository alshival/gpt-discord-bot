# GPT-Discord-Bot Starter Code

Welcome to the Discord Bot Starter Code brought to you by [Alshival's Data Service](https://alshival.com). This code utilizes [OpenAI](https://openai.com/) to provide a simple, yet expandable bot framework, allowing you to get started swiftly. Currently, we've implemented two models:

  * `text-davinci-002`: An economical choice suitable for a Discord server with a large user base. OpenAI does offer lighter models that might suit your requirements as well.
  * `gpt-3.5-turbo`: A more powerful option, ideally suited for $\huge\textcolor{red}{\textbf{\textsf{tutoring study groups}}}$ or $\huge\textcolor{green}{\textbf{\textsf{brainstorming with small teams}}}$.

We'll incorporate a `!GPT4` command once GPT-4 scales up. The bot's code is designed to let you switch models effortlessly, even to fine-tuned models. To explore all available options, visit the [OpenAI's models](https://platform.openai.com/docs/models) page. You can have this bot up and running in $\huge\textcolor{VioletRed}{\textsf{just 7 steps}}$.

For assistance in building more complex bots, integrating the bot with your data using a fine-tuned model, or training it for document search, please visit [Alshival.com](https://alshival.com).

Remember, while using this bot, data privacy laws may apply in certain cases like Q&A bots for legal or medical documents. A self-hosted solution would be required rather than Discord for such use cases.

Please note that the basic bot does not remember conversations. Also, the `!chatGPTturbo` command might take a few seconds to execute.

## **Update 2023-05-15: `gpt_discord_bot_v2.py`** 
We've upgraded our `gpt_discord_bot.py` to `gpt_discord_bot_v2.py`. This version enhances `!chatGPTturbo` by integrating a SQLite3 database for memory storage, enabling the bot to maintain memories of conversations within a channel. It stores up to 200 interactions, but this can be customized. The bot now recalls the last four interactions, regardless of the submitter or the model used. This means you can use `!chatGPT`, then continue the conversation using `!chatGPTturbo`. These settings can be adjusted in the code.

Prompts and Responses are stored in the sqlite database `data.db` under the `prompts` table.

This version also includes a `!reminder` function for scheduling reminders. 

```
!reminder 2023-05-16 14:15 Take a break!
```

These reminders are stored in the sqlite database `data.db` under the `reminders` table.

Currently, memory support is not available with `!chatGPT`. The `!GPT4` command will be incorporated once GPT-4 exits the beta phase, providing enhanced memory capabilities.

Bear in mind, Discord imposes a 2,000-character limit for inputs. Please note, this bot doesn't check for token limits due to the incompatibility of the `tiktoken` package with newer Python versions on certain platforms, like the one installed on my Chromebook. Including historical messages might lead you to hit this limit.

In this example, we use the bot to schedule a reminder to take a break using the `!reminder` command. Then we ask a question using `!chatGPT` and access the memory of the conversation via `!chatGPTturbo`. [We are working on scheduling reminders using natural language.]

<p align="center">
<img src="https://github.com/alshival/gpt-discord-bot/blob/main/.meta/gpt-discord-bot-v2%20(5).png?raw=true" width="75%" height="75%">
</p>

# Usage
To use `text-davinci-002` in Discord, prefix your request with `!chatGPT`.

<p align="center">
    <img src="https://github.com/alshival/gpt-discord-bot/blob/main/.meta/Screenshot%202023-05-05%204.16.58%20AM.png?raw=true">
</p>

For `gpt-3.5-turbo` usage in Discord, prefix your request with `!chatGPTturbo`.

<p align="center">
    <img src="https://github.com/alshival/gpt-discord-bot/blob/main/.meta/Screenshot%202023-05-05%2011.50.53%20PM.png?raw=true">
</p>
A little side note... Salski and I prefer using USB ports or RJ-45... but as they say, to each their own.

Here's a case study: A data science student sought my help on UpWork for their homework. I assisted them with their graph theory problems, then suggested they use GPT for the remaining probability and calculus problems. Knowing GPT's capabilities, I recommended them to form a study group and gave them a link to this bot. It proved to be an excellent tutoring tool, and also a cost-effective solution for the students.

The beauty of learning AI is that you can use AI itself to facilitate your learning. As a mathematician, I was amazed by the proficiency of these models. After verifying a few results, I felt confident enough to recommend it to the students.

<p align="center">
<img src="https://github.com/alshival/gpt-discord-bot/blob/main/.meta/Screenshot%202023-05-12%202.37.22%20AM.png?raw=true" width="50%" height="50%">
</p>

# Installation

In order for the bot to respond, it must be running on a machine such as a cloud server, a PC or laptop, or even a Raspberry Pi tucked away in your bedroom (a hint for students on a tight budget).

You'll need a Python installation (students, we suggest getting JupyterLab as well) and an [OpenAI API key](https://platform.openai.com/account/api-keys).

### Step 1
Create a Discord account if you haven't already.

### Step 2
Set up a new Discord application at the [Discord Developer Portal](https://discord.com/login?redirect_to=%2Fdevelopers%2Fapplications). After logging in, click on the "New Application" button, name your application, and hit "Create."

### Step 3
Create a bot for your Discord application by clicking on the "Bot" tab and then "Add Bot." Name your bot and click "Create."

### Step 4
Generate a token for your bot by clicking on the "Copy" button next to "Token" under the bot's name. Keep this token secure as it's needed to authenticate your bot with the Discord API.

### Step 5
Install the necessary dependencies, which are the Discord.py and OpenAI Python modules. Install them via pip by running the following command in your terminal:

```
pip install discord.py openai
```

### Step 6
Set the environment variables `OPENAI_API_KEY` (your actual OpenAI API key) and `DISCORD_BOT_TOKEN` (the token you generated). On Linux, you can do this by editing your `~/.bashrc` file:

```
export OPENAI_API_KEY="<API KEY>"
export DISCORD_BOT_TOKEN="<BOT TOKEN>"
```
Replace `<API KEY>` with your OpenAI API key and `<BOT TOKEN>` with the token you created in Step 4.

You can edit your `~/.bashrc` file using a command-line text editor like nano on a Raspberry Pi. 

```
nano ~/.bashrc
```
Make your changes and hit Ctrl+X to save and close.

### Step 7
Launch your bot by executing the following command in your terminal:

```
python gpt_discord_bot.py
```

Or for version 2:

```
python gpt_discord_bot_v2.py
```

Congratulations! Your bot should now be up and running! You can invite it to your Discord server by going back to the Discord Developer Portal, selecting your application, clicking on the "OAuth2" tab, selecting the "bot" scope, then choosing the text permissions you need, and finally, copying the generated OAuth2 URL into your browser.

With this simple installation process, you are all set to explore the world of AI-driven chatbots. Happy coding!

Remember, this is just a starting point. As you grow more comfortable with the bot and its capabilities, feel free to make modifications and enhancements to better meet the needs of your community. Happy coding!
