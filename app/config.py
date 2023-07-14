import os
import discord
from discord.ext import commands,tasks

# Set up Discord Bot token here:
discord_bot_token = os.environ.get("DISCORD_BOT_TOKEN")

import pandas as pd
from datetime import datetime, timedelta
import json
############################################
# openai API config 
############################################
import openai
# Set up the OpenAI API. The key is stored as an environment variable for security reasons.
openai.api_key = os.environ.get("OPENAI_API_KEY")

############################################
# Youtube Data API config
############################################
import yt_dlp
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
# Set up the Google Youtube Data API key. For youtube searching and playback.
google_api_key = os.environ.get("google_api_key")

# Set up the YouTube Data API client
youtube = build("youtube", "v3", developerKey=google_api_key)

#############################################
# KERAS LAYER - Task Assignment
#############################################
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Embedding, GlobalMaxPooling1D
from tensorflow.keras.optimizers import Adam
# Number of training epochs for the keras layer.
epochs = 25


# Define the labels for task assignment in the Keras model
keras_labels = ['other', 'reminder', 'youtube']

# Note for developers:
# When adding new features that require task assignment in the Keras model,
# make sure to update this list of labels accordingly in conjunction with the changes made in app/keras_layer.py.

############################################
# database config
############################################
import sqlite3
import aiosqlite
import asyncio

# Where you wish to store the bot data.
db_name = 'app/data.db'

# Number of prompts stored in the local SQLite database. The table is truncated when the bot starts up.
prompt_table_cache_size = 200

# This function establishes a global connection to the 'data.db' SQLite database.
# It is used by some other functions whenever they need to interact with the database.
async def create_connection():
    return await aiosqlite.connect(db_name)