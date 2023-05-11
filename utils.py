import io
import fitz
from PIL import Image

def is_void(color: tuple[int]) -> bool:
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

def craft(day_index: int, path = 'menu.pdf') -> None:
    '''
    Craft a table.jpg and a current.jpg image from the pdf
    stored in path.
    '''

    #& Convert PDF to image

    doc: fitz.Document = fitz.open(path)
    raw = doc[0].get_pixmap(dpi = 120).tobytes()
    page = Image.open(io.BytesIO(raw))

    #& Find table paddings

    left = walk(page, [0, page.size[1] // 2], 'x') + 2
    top = walk(page, [left, 0], 'y') + 2

    right = walk(page, [page.size[0] - 1, page.size[1] // 2], '-x') - 1
    bottom = walk(page, [left, page.size[1] - 1], '-y') - 1

    #& Crop table

    table = page.crop(( left, top, right, bottom ))
    table.save('table.jpg')

    #& Get column length

    column = table.size[0] / 5

    #& Parse specific day

    crop = table.crop((
        column * day_index, 0,
        column * (day_index + 1), table.size[1]
    ))
    
    crop.save('current.jpg')

# EOF