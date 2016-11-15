#!/usr/bin/env python3

from datetime import datetime, timedelta
import re

import star_barcode

tomorrow = datetime.today() + timedelta(1)

barcode_path = star_barcode.barcode_from_date(tomorrow)
week, sequence = re.search(r'Barcode_\d{4}-W(\d{2})-\d{1}_(\d{2}).pdf',
                           'Barcode_2016-W46-3_23.pdf').groups()

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

with open('check_page.html', encoding='utf-8') as template_file:
    html_template = template_file.read()

formatted_html = html_template.format(
    date=tomorrow,
    sequence=sequence,
    week=week,
    tablerows=''.join(table_rows))

with open('index.html', mode='w', encoding='utf-8') as index_file:
    index_file.write(formatted_html)
