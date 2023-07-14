from app.config import *
from app.bot_functions import *
from app.keras_layer import classify_prompt

# For creating reminders
from app.fefe_create_reminder import *
# For general discussion
from app.fefe_openai import *
# For searching youtube
from app.fefe_youtube import *

async def talk_to_fefe(ctx, message,bot):

    model = "gpt-3.5-turbo"
    
    db_conn = await create_connection()
    username = ctx.author.name
    
    channel_name = ctx.channel.name
    try:
        message_category = await classify_prompt(message)
        message_classified =True
    except Exception as e:
        # Capture the error message
        error_message = str(e)
        print(type(message))
        print(message)
        await ctx.send(f"""
        I'll need a bit more training to answer your question.
        Run `!label_last <label>` by replacing '<label>' with one of the following request types: {str(keras_labels)}. Then run `!retrain_keras`.
        """)
        await store_prompt(db_conn, ctx.author.name, message, model,'', channel_name,keras_classified_as = 'ERROR')
        return

    # bot's Reminder Capabilities
    if message_category == 'reminder':
        await set_reminder(ctx,message,model,db_conn)
    # Bot's openAi capabilities
    elif message_category == 'other':
        await fefe_openai(ctx,message,model,db_conn)
    
    # Bot's youtube capabilities
    elif message_category == 'youtube':
        await fefe_youtube(bot,ctx,message,model,db_conn)