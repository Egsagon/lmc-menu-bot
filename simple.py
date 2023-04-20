import io
import re
from datetime import datetime

import discord
import fitz
import requests
from discord.ext import tasks
from PIL import Image


# Settings
dpi = 100
source = 'current.jpg'
ps1 = '\033[93m♪\033[0m'
client = discord.Client(intents = discord.Intents.all())
root = 'http://www.lyc-curie-versailles.ac-versailles.fr/'


@client.event
async def on_ready() -> None:
    print(ps1, 'Bot started')
    
    looper.start()

@tasks.loop(minutes = 10)
async def looper() -> None:
    '''
    Cycle fetch current day.
    '''
    
    global cache
    
    print(ps1, 'Fetching menu from source... ', end = '')
    
    # Find today
    index = datetime.now().weekday()

    # Fetch page
    raw = requests.get(root + 'spip.php?rubrique186').text

    # Parse url
    imenu, index = (0, index) if index <= 5 else (1, 0)
    src = re.findall(r'href=\"(IMG/pdf/menu.*?)\"', raw)[imenu]
    
    # Fetch ressource
    raw = requests.get(root + src).content
    
    # Save ressource
    with open('menu.pdf', 'wb') as temp:
        temp.write(raw)
    
    # Load document as image
    doc: fitz.Document = fitz.open('menu.pdf')
    raw = doc[0].get_pixmap(dpi = dpi).tobytes()
    box = Image.open(io.BytesIO(raw))
    
    # Crop image
    pad = index * 217.5
    img = box.crop((42 + pad, 162, 260 + pad, 570))
    
    # Save result
    img.save(source)
    
    print('done.')


@client.event
async def on_message(msg: discord.Message) -> None:
    '''
    Handle message reception.
    '''
    
    if not msg.content.startswith('?menu'): return
    print(ps1, f'Sending menu to \033[92m{msg.author}\033[0m.')
    
    path = 'menu.pdf' if 'all' in msg.content else source
    
    with open(path, 'rb') as file:
        await msg.reply('**Menu:**', file = discord.File(file))


if __name__ == '__main__':
    client.run('MTA5ODI0NDc5MzI0ODc4NDQ0NA.G3aYh9.1v5gfWwCWEIm8M_10jhg2l00iFE6IRYVXVRp5o')