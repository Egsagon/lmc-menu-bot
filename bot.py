'''
LMC Menu Bot
'''

import io
import core
import discord
import logging

PS1 = '\033[92m$ \033[0m'
TOKEN = open('token').read()

bot = discord.Client(intents = discord.Intents.all())

@bot.event
async def on_ready() -> None:
    '''
    Initialises the bot.
    '''
    
    print(PS1, 'Bot ready.')
    await bot.change_presence(status = discord.Status.do_not_disturb)

@bot.event
async def on_message(msg: discord.Message) -> None:
    '''
    Handle commands reception.
    '''
    
    raw: str = msg.content
    
    # Avoid treating unrelated messages
    if not raw.startswith('?menu'): return
    
    # Display menu
    today = core.today()
    
    if not 0 < today.weekday() < 5:
        return await msg.reply('We do not eat today.')
    
    # Get data and image
    week = core.get_week_url(today)
    day = None if 'all' in raw else today.weekday()
    image = core.parse(week, day)
    
    # Save the image to a buffer and send it
    with io.BytesIO() as buffer:
        
        image.save(buffer, 'png')
        buffer.seek(0)
        
        print(PS1, 'Sending menu to', msg.author)
        await msg.reply(file = discord.File(buffer, 'img.png'))


if __name__ == '__main__':
    bot.run(TOKEN, log_level = logging.ERROR)

# EOF