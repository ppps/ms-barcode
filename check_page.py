#!/usr/bin/env python3

from datetime import datetime, timedelta
from pathlib import Path
import re
import sys

import star_barcode

try:
    directory = Path(sys.argv[1]).resolve()
except IndexError:
    directory = Path('./').resolve()

tomorrow = datetime.today() + timedelta(1)

barcode_path = star_barcode.barcode_from_date(
    date=tomorrow, output_dir=directory)
week, sequence = re.search(r'Barcode_\d{4}-W(\d{2})-\d{1}_(\d{2}).pdf',
                           barcode_path.name).groups()

tr_template = '''\
    <tr>
      <td>{d:%V}</td>
      <td>{d:%B %-d %Y}</td>
    </tr>
'''

monday_of_week = tomorrow - timedelta(tomorrow.isoweekday() - 1)
previous_monday = monday_of_week - timedelta(7)

table_rows = [
    tr_template.format(d=previous_monday + timedelta(7 * i))
    for i in range(4)
    ]

template_path = str(Path(__file__).parent.joinpath('check_page.html'))

with open(template_path, encoding='utf-8') as template_file:
    html_template = template_file.read()

formatted_html = html_template.format(
    date=tomorrow,
    barcodepath=barcode_path.name,
    sequence=sequence,
    week=week,
    tablerows=''.join(table_rows))


index_path = str(directory.joinpath('index.html'))
with open(index_path, mode='w', encoding='utf-8') as index_file:
    index_file.write(formatted_html)
