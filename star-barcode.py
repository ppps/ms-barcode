#!/usr/bin/env python3

import treepoem
from PIL import Image, ImageDraw, ImageFont

issn = '0307-1758'
sequence = '21'
variant = '44'

barcode = treepoem.generate_barcode(
    barcode_type='issn',
    data=' '.join([issn, sequence, variant]),
    options={'includetext': True,
             'height': 1.28})

barcode.load(scale=2)
barcode = barcode.convert('1')
# barcode = barcode.crop((0, 37, *barcode.size))

base = Image.new(
    mode='1',
    size=(barcode.size[0] + 10, barcode.size[1] + 15),
    color=1)
txt = Image.new(mode='1', size=(barcode.size[0], 45), color=1)

font = ImageFont.truetype('/Library/Fonts/MyriadPro-Regular.otf', 40)
d = ImageDraw.Draw(txt)
d.text((10, 0), 'MSTAR • 20161109 • WED', font=font)

base.paste(barcode, (10, 15))
base.paste(txt, (37, 0))

base.save('bc.tiff', dpi=(316, 316))

