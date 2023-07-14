from app.config import *
from app.bot_functions import *

async def search_youtube(ctx, *, query):
    try:
        # Call the search.list method to search for videos
        search_response = youtube.search().list(
            q=query,
            part="id,snippet",
            maxResults=3
        ).execute()

        # Create a formatted string with the video titles
        video_titles = "\n".join(
            f"""[{search_result["snippet"]["title"]}](https://www.youtube.com/watch?v={search_result["id"]["videoId"]})"""
            for search_result in search_response.get("items", [])
            if search_result["id"]["kind"] == "youtube#video"
        )

        # Send the video titles as a message in the Discord channel
        await ctx.send(f"Search results for '{query}':\n{video_titles}")

    except HttpError as e:
        await ctx.send("An HTTP error occurred.")
        print("An HTTP error occurred:")
        print(e)

#These are options for the youtube dl, not needed actually but are recommended
ytdlopts = { 
    'format': 'bestaudio/best',
    'outtmpl': 'app/downloads/%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',  
    'force-ipv4': True,
    'preferredcodec': 'mp3',
    'cachedir': False
    
    }

ffmpeg_options = {
        'options': '-vn'
    }

ytdl = yt_dlp.YoutubeDL(ytdlopts)

async def fefe_youtube(bot,ctx,message,model,db_conn):
    try:
        voice_channel = ctx.author.voice.channel #checking if user is in a voice channel
    except AttributeError:
        await store_prompt(db_conn, ctx.author.name, message, model, '', ctx.channel.name,keras_classified_as='youtube')
        return await ctx.send("Join a voice channel and ask me again.") # member is not in a voice channel
        
    permissions = voice_channel.permissions_for(ctx.me)
    if not permissions.connect or not permissions.speak:
        await store_prompt(db_conn, username, message, model, '', channel_name,keras_classified_as='youtube')
        await ctx.send("I don't have permission to join or speak in that voice channel.")
        return
        
    messages = [{'role':'user','content':'Return a youtube search query based on the following message: Play spirit in the sky'},
               {'role':'assistant','content':'Spirit in the Sky'},
               {'role':'user','content':'Return a youtube search query based on the following message: Play the Lion King song'},
               {'role':'assistant','content':"I just can't wait to be king"},
               {'role':'user','content':'Return a youtube search query based on the following message: ' +message}]
    response = openai.ChatCompletion.create(
        model=model,
        messages = messages,
        max_tokens=1024,
        n=1,
        temperature=0.5,
        top_p=1
    )
    response_text = response['choices'][0]['message']['content']
    
    try:
        # Call the search.list method to search for videos
        search_response = youtube.search().list(
            q=response_text,
            part="id,snippet",
            maxResults=1
        ).execute()
        search_result = [x for x in search_response.get("items",[]) if x["id"]["kind"] == "youtube#video"][0]
        
        video_url = f"""https://youtu.be/{search_result["id"]["videoId"]}"""
        video_title = f"""### {search_result["snippet"]["title"]}"""
        
    except HttpError as e:
        await ctx.send("An HTTP error occurred.")
        print("An HTTP error occurred:")
        print(e)
        
    voice_client = ctx.guild.voice_client
    if not voice_client:
        await voice_channel.connect()
        voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    
    loop = asyncio.get_event_loop()
    data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url=video_url, download=True)) #extracting the info and not downloading the source
        
    title = data['title'] #getting the title
    song = data['url'] #getting the url
    
    if 'entries' in data: #checking if the url is a playlist or not
        data = data['entries'][0] #if its a playlist, we get the first item of it
    try:
        voice_client.play(discord.FFmpegPCMAudio(source=song,**ffmpeg_options, executable="ffmpeg")) #playing the audio
    except Exception as e:
        print(e)
    
    await ctx.send(f"### Playing: {title}\n{video_url}")

        # Store the new prompt and response in the 'prompts' table
    await store_prompt(db_conn, ctx.author.name, message, model, response_text, ctx.channel.name,keras_classified_as='youtube')
