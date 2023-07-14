from app.config import * 
from app.bot_functions import *

async def set_reminder(ctx,message,model,db_conn):
    messages = []
    messages.extend([{'role':'user','content':'remind me to turn in my homework next week in the morning.'},
                    {'role':'assistant','content':"""{"message":"Turn in homework","reminder_time":"(datetime.now() + timedelta(weeks=1)).strftime('%Y-%m-%d 09:00:00')"} """}])
    messages.extend([{'role': 'user', 'content': "Remind me in three hours to pick up the kids."},
                  {'role': 'assistant', 'content': """{"message":"Pick up the kids","reminder_time":"(datetime.now() + timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:00')"} """}])
    messages.extend([{'role': 'user', 'content': 'Remind me to buy groceries tomorrow.'},
                    {'role': 'assistant', 'content': """{"message":"Buy groceries","reminder_time":"(datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:00')"} """}])
    messages.extend([{'role': 'user', 'content': 'Remind me in 30 minutes to call my mom.'},
                     {'role': 'assistant', 'content': """{"message":"Call mom","reminder_time":"(datetime.now() + timedelta(minutes=30)).strftime('%Y-%m-%d %H:%M:00')"} """}])
    messages.append({'role':'user','content':f'Put this in the same format as before: {message}'})
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,        
        max_tokens=1024,
        n=1,
        temperature=0.5,
        top_p=1,
        frequency_penalty=0.0,
        presence_penalty=0.6,
    )
    
    # Extract the response text and send it back to the user
    response_text = response['choices'][0]['message']['content']
    try:
        response_text = eval(response_text)
    
        reminder_time = eval(response_text['reminder_time'])
    except Exception as e:
        await ctx.send(response_text)
    
    dictionary = {
        'message': response_text['message'],
        'response_time': reminder_time
    }
    
    await store_prompt(db_conn, ctx.author.name, message, model, f"Reminder set for {reminder_time}.", ctx.channel.name,keras_classified_as='reminder')
    
    # Add the new reminder to the database
    await add_reminder(ctx.author.name, response_text['message'], ctx.channel.id, ctx.channel.name, reminder_time)
    await ctx.send(f"Reminder set for {reminder_time}.")
