import re
import time
import requests

import discord
from discord.ext import tasks
from datetime import datetime

import utils

# Settings
TRIGGER = '?menu'
TOKEN = 'ENTER DISCORD BOT TOKEN HERE'

# Initialise client
bot = discord.Client(intents = discord.Intents.all())
root = 'http://www.lyc-curie-versailles.ac-versailles.fr/'

stat_start = datetime.now()
stat_weeks = 0
stat_avg = 0
last_run: str = None

@bot.event
async def on_ready() -> None:
    '''
    Initiator.
    '''
    
    print('Bot Started')
    crafter.start()
    
    # To set custom message
    await bot.change_presence(status = discord.Status.do_not_disturb)

@tasks.loop(hours = 24)
async def crafter() -> None:
    '''
    Cycle regenerating ressources each day.
    '''
    
    start = time.time()
    
    global stat_weeks, stat_avg, last_run
    
    print('Updating ressource... ', end = '')
    
    day = datetime.now().weekday()
    
    # Fetch ressource url
    raw = requests.get(root + 'spip.php?rubrique186').text
    src = re.findall(r'href=\"(IMG/pdf/menu.*?)\"', raw)[day > 4]
    
    # Save ressource
    with open('menu.pdf', 'wb') as temp:
        temp.write(requests.get(root + src).content)
    
    # Craft
    utils.craft(day)
    print('done.')
    
    # Update stats
    stat_weeks += 1
    stat_avg += time.time() - start
    last_run = datetime.now().strftime('%d/%m/%Y - %Hh%M')

@bot.event
async def on_message(msg: discord.Message) -> None:
    '''
    Handle commands receiption.
    '''
    
    if not msg.content.startswith(TRIGGER): return
    args = msg.content.split()[1:]
    
    match args:
        
        case ['info']:
            # Post stats
            
            runtime = round((datetime.now() - stat_start).total_seconds(), 3)
            avg = round(stat_avg / stat_weeks, 3)
            
            await msg.reply(
                '`IO v.0.6`\n' + \
                f'`Running for {runtime}s`\n' + \
                f'`Parsed {stat_weeks} ressources`\n' + \
                f'`Average parsing time: {avg}s`'
            )
        
        case [*opts]:
            # Post the menu
            
            print(f'Sending menu for \033[92m{msg.author}\033[0m')
            
            path = 'table.jpg' if 'all' in opts else 'current.jpg'
            await msg.reply(f'**Menu:** (last updated *{last_run}*)',
                            file = discord.File(path))
        
        case unknown:
            # Error return
            await msg.reply(f'Invalid command: `{unknown}`')


if __name__ == '__main__': bot.run(TOKEN)

# EOF