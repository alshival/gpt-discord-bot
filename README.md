# openAi Discord Bot: Transforming Discord into a Virtual Study Room and Workspace

Welcome to the openAi Discord Bot brought to you by [Alshival's Data Service](https://Alshival.com). This code utilizes [OpenAI](https://openai.com/) and Tensorflow to provide a simple, yet expandable bot framework, allowing you to get started swiftly. It allows you to use openAi's models from within discord and set reminders using natural language.

You can also ask it to play tic tac toe with you.

Check a video of the bot in action here, and how to improve task classification by the keras layer from within Discord: [Youtube](https://youtu.be/RhjecZdwxZc).

Please report any [issues via github](https://github.com/alshival/gpt-discord-bot/issues) or contact [Alshival's Data Service](mailto:support@alshival.com?subject=gpt-discord-bot%20error)

Currently, we've implemented two models:

  * `text-davinci-003`: An economical choice suitable for a Discord server with a large user base. OpenAI does offer lighter models that might suit your requirements as well.
  * `gpt-3.5-turbo`: A more powerful option, ideally suited for $\huge\textcolor{red}{\textbf{\textsf{tutoring study groups}}}$ or $\huge\textcolor{green}{\textbf{\textsf{brainstorming with small teams}}}$.

We'll incorporate a `!GPT4` command once GPT-4 scales up. The bot's code is designed to let you switch models effortlessly, even to fine-tuned models. To explore all available options, visit the [OpenAI's models](https://platform.openai.com/docs/models) page. You can have this bot up and running in $\huge\textcolor{VioletRed}{\textsf{just 7 steps}}$.

Note that training the keras layer is required, but we've streamlined the process so that you can do it right from Discord.

# Usage


To use `text-davinci-003` in Discord, prefix your request with `!davinci3`.

```
!davinci3 What are some historical events that took place in 1279?
```

For `gpt-3.5-turbo` usage in Discord, prefix your request with `!gpt3`.

```
!gpt3 Write python code to move the axis of a CNC machine using a USB port. (please... no more parallel ports...)
```

In order to minimize reliance on openAi, a keras layer for relaying requests was added before `gpt-3.5-turbo`.  Still, their models do most of the heavy lifting. This is what allows our bot to create reminders using natural language. Each time you use a model command, the openAi model is used only once to obtain the end result. The tic tac toe games requires openAi to make a decition each time they make a move.

To schedule a reminder, use `!reminder YYYY-MM-DD HH:MM <REMINDER>`:

```
!reminder 2023-05-16 14:15 Take a break!
```

or use natural language with `gpt3`:

<p align="center">
<img src="https://github.com/alshival/gpt-discord-bot/blob/main/.meta/gpt-discord-bot-v2%20(5).png?raw=true" width="100%" height="100%">
</p>

Notice how memories are accessed by the bot across different models. `gpt3` is asked to continue where `davinci3` left off. This is a benefit of using the SQLite3 database.

You can also have the bot play tic tac toe with you. GPT makes the move.


<p align="center">
<img src="https://github.com/alshival/gpt-discord-bot/blob/main/.meta/Screenshot%202023-05-18%205.37.17%20AM.png" width="100%" height="100%">
</p>

# Training the keras layer

You will need to teach the keras layer for some time when you install the bot. I provided a very small amount of training data. If you ask it to do a task and the bot misbehaves, such as when you meant to schedule a reminder and it starts tic tac toe or gives you a generated answer, include the last prompt in the training data using `label_last` along with the appropriate label (end a tic tac toe game first by entering random string):

```
!label_last reminder
!label_last other
!label_last ttt
```

* `reminder` - Used if you were asking it to schedule a reminder.
* `other` - Used if you asked it a general question and want to access GPT directly.
* `ttt` - Used if you wanted to play tic tac toe.

Finally, run `!retrain_keras` to retrain the model after adding your prompt. `!retrain_keras` requires administative privileges. 
The keras layer is always retrained when the bot boots up.

<p align="center">
<img src="https://github.com/alshival/gpt-discord-bot/blob/main/.meta/Screenshot%202023-05-18%205.14.19%20AM.png?raw=true" width="100%" height="100%">
</p>

`label_last` is user and channel specific. Let us know if you run into any bugs by submitting a [new issue](https://github.com/alshival/gpt-discord-bot/issues).

For those of you who would like us to host your bot, or if you would like customized solutions, visit our little shop: [Alshival.com](https://Alshival.com).

For assistance in building more complex bots, integrating the bot with your data using a fine-tuned model, or training it for document search, please visit [Alshival.com](https://Alshival.com).

<sup><sub>
Disclaimer: Alshival's Data Service is not affiliated with Kiki's Delivery Service. <br>
Discord is great, though may not satisfy requirements set by data privacy laws, such as for Q&A bots for legal or medical documents. In these cases, a self-hosted front-end solution may be required. Visit [Alshival's Data Service](https://alshival.com) for more information. <br>
Note that the `!gpt3` command might take a few seconds to execute. Note that Discord imposes a 2,000-character limit for inputs. Note further this bot doesn't check for token limits due to the incompatibility of the `tiktoken` package with newer Python versions on certain platforms, like the one installed on my Chromebook. <br>
Therefore, note that historical messages might lead you to hit this limit.
</sup></sub>

# Case Study

Here's a case study: A data science student sought my help on UpWork for their homework. I assisted them with their graph theory problems, then suggested they use GPT for the remaining probability and calculus problems. Knowing GPT's capabilities, I recommended them to form a study group and gave them a link to this bot. It proved to be an excellent tutoring tool, and also a cost-effective solution for the students.

The beauty of learning AI is that you can use AI itself to facilitate your learning. As a mathematician, I was amazed by the proficiency of these models. After verifying a few results, I felt confident enough to recommend it to the students.

# Installation

In order for the bot to respond, it must be running on a machine such as a cloud server, a PC or laptop, or even a Raspberry Pi tucked away in your bedroom (a hint for students on a tight budget).

<p align="center">
<img src="https://github.com/alshival/gpt-discord-bot/blob/main/.meta/20230516_183603.gif?raw=true" width="100%" height="100%">
</p>

### Step 0
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
Install the necessary dependencies via the command line:

```
pip install discord openai datetime json sqlite3 aiosqlite asyncio numpy tensorflow
```

For the basic bot without memory capabilities (`gpt_discord_bot.py`), you only need to install the following packages:

```
pip install discord openai
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
python3 gpt_discord_bot_v2.py
```

or for the basic bot without memory capabilities:

```
python gpt_discord_bot.py
```

Congratulations! Your bot should now be up and running! You can invite it to your Discord server by going back to the Discord Developer Portal, selecting your application, clicking on the "OAuth2" tab, selecting the "bot" scope, then choosing the text permissions you need, and finally, copying the generated OAuth2 URL into your browser.

With this simple installation process, you are all set to explore the world of AI-driven chatbots. Happy coding!

Remember, this is just a starting point. As you grow more comfortable with the bot and its capabilities, feel free to make modifications and enhancements to better meet the needs of your community. Happy coding!

```
DONE: Rebuilt locally from scratch. Bot is starting up smoothly now. 
* TO DO: Start on v3, improving on v2. Code so that it can handle multiple guilds.
* TO DO: provide starter database for training the keras layer. labeled_prompts will be included in there for further training. 
* TO DO: Add ability to cancel reminders.
* TO DO: Consider a Federated Learning Model for the keras layer.
* To DO: Cache training data for tic tac toe game. The Ai should get better as time goes on.
       To this, I have some ideas. We collect the data for the games. Store each state of the board
       in the SQLite database. After a match is complete, we label matches openAi wins with 1, 
       and those which resulted in a draw with 0, and those which resulted in a loss with -1.
       That is then included int the training data for the GPT model.
       We could also try training another layer in-house to do that part, but I really want to see how far I can push openAi.
```
