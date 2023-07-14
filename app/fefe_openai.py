from app.config import *
from app.bot_functions import *

async def fefe_openai(ctx,message,model,db_conn):
    past_prompts = await fetch_prompts(db_conn, ctx.channel.name, 5)  # Fetch the last 5 prompts and responses
    messages = []
    # Construct the messages parameter with the past prompts and responses and the current message
    for prompt, response in past_prompts:
        messages.extend([{'role': 'user', 'content': prompt}, {'role': 'assistant', 'content': response}])
    messages.append({'role': 'user', 'content': message})

    # Generate a response using the 'gpt-3.5-turbo' model
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
    if len(response_text) > 2000:
        await send_chunks(ctx, response_text)
    else:
        await ctx.send(response_text)

    # Store the new prompt and response in the 'prompts' table
    await store_prompt(db_conn, ctx.author.name, message, model, response_text, ctx.channel.name,keras_classified_as='other')
    await db_conn.close()