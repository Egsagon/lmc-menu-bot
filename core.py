import re
import requests
import pypdfium2 as pypdf

import io
import dateparser
from PIL import Image
from datetime import datetime


ROOT = 'http://www.lyc-curie-versailles.ac-versailles.fr/'

# Regexes compilation
re_pdf_url = re.compile( r'href=\"(IMG/pdf/menu.*?)\"' )
re_pdf_date = re.compile( r'du_(.*?)_au_(\d*)_(.*?)\.pdf' )

def today() -> datetime:
    '''
    Return today's date.
    '''
    
    return datetime.today().date()

def get_week_url(rel: datetime) -> str | None:
    '''
    Fetch weeks and returns a pdf URL.
    '''
    
    # Get body page and PDF urls
    body = requests.get(ROOT + 'spip.php?rubrique186').text
    files = re_pdf_url.findall(body)
    
    for file in files:
        # Parse boundary dates
        start, end, date = re_pdf_date.findall(file)[0]
        parse = lambda day: dateparser.parse(f'{day}_{date}').date()
        
        # Check if relative is included in week
        if parse(start) <= rel <= parse(end): return file
    
    return

def is_void(color: tuple[int]) -> bool:
    '''
    Decide whether a pixel is considered empty
    '''
    
    return all([ c > 250 for c in color ])

def walk(image: Image, start: tuple[int], direction: str) -> tuple[int]:
    '''
    Simulate a pointer walking from a point in a certain direction
    until it touches something.
    '''
    
    coords = start
    
    index = int('y' in direction)
    factor = -1 if '-' in direction else 1
    
    while is_void(image.getpixel(tuple(coords))):
        image.putpixel(tuple(coords), (0, 255, 0))
        coords[index] += factor
    
    return coords[index]

def parse(url: str, day: int | None) -> Image.Image:
    '''
    Fetch a PDF and extract a day of the whole week out of it.
    '''
    
    # Load PIL Image
    raw = requests.get(ROOT + url).content
    pdf = pypdf.PdfDocument(raw)
    img = pdf[0].render().to_pil()
    
    # Fetch table coordinates
    x, y = img.size
    
    l = walk(img, [0,     y // 2], 'x')  + 2
    t = walk(img, [l,     0     ], 'y')  + 2
    r = walk(img, [x - 1, y // 2], '-x') - 1
    b = walk(img, [l,     y - 1 ], '-y') - 1
    
    # Crop table
    table = img.crop((l, t, r, b))
    
    # Return the whole week
    if day is None:
        return table
    
    # Return a specific day
    x, y = table.size
    col = x / 5
    
    part = table.crop(( col * day, 0,
                        col * (day + 1), y ))
    
    return part

# EOF