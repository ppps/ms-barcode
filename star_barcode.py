#!/usr/bin/env python3

from datetime import datetime, timedelta
from pathlib import Path
import subprocess

BWIPP = Path(__file__).resolve().parent.joinpath('bwipp', 'barcode.ps')
ISSN = '0307-1758'
PRICE_CODES = [None, 2, 2, 2, 2, 2, 3, 2]  # Indexed to ISO weekday
PRICES = [None, None, 1.0, 1.2]  # Indexed to price codes (0 & 1 not used)


def asrun(ascript):
    "Run the given AppleScript and return the standard output and error."
    osa = subprocess.Popen(['/usr/bin/osascript', '-'],
                           stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.DEVNULL)
    return osa.communicate(ascript)[0]


# This borrowed from http://stackoverflow.com/questions/304256
# while we wait for Python to introduce ISO year, week and day
# directives, which are coming at the end of 2016 in 3.6.
def iso_year_start(iso_year):
    "The gregorian calendar date of the first day of the given ISO year"
    fourth_jan = datetime(iso_year, 1, 4)
    delta = timedelta(fourth_jan.isoweekday()-1)
    return fourth_jan - delta

def iso_to_gregorian(iso_year, iso_week, iso_day):
    "Gregorian calendar date for the given ISO year, week and day"
    year_start = iso_year_start(iso_year)
    return year_start + timedelta(days=iso_day-1, weeks=iso_week-1)


tomorrow = datetime.today() + timedelta(1)
iso_year, iso_week, iso_day = tomorrow.isocalendar()

# Sequence is a two-digit number: XY
# X is the price code, Y is the ISO day of the week
sequence = (PRICE_CODES[iso_day] * 10) + iso_day

# TODO: Prompt the user to confirm
sequence = sequence
iso_week = iso_week
iso_year = iso_year  # Which year is the nearest Thursday in?

# TODO: This needs to go when 3.6 is released
edition_date = iso_to_gregorian(iso_year, iso_week, sequence % 10)

# TODO: Upgrade to Python 3.6 and use this version
# edition_date = datetime.strptime(
#    '{G}-W{V}-{u}'.format(G=iso_year, V=iso_week, u=sequence % 10),
#    '%G-W%V-%u'
#    )

def barcode_header(date, price):
    template = 'MSTAR {date:%Y-%m-%d} {date:%a} {price:.1f}'
    return template.format(date=date, price=price).upper()

header_string = barcode_header(
    date=edition_date,
    price=PRICES[sequence // 10]
    )

issn_args = ' '.join([ISSN, str(sequence), str(iso_week)])
barcode_file = 'Barcode_{0}-W{1}-{2}_{3}.pdf'.format(
    *edition_date.isocalendar(),
    sequence
    )

postscript = '''\
%!PS
({bwipp_location}) run

11 5 moveto ({issn_args}) (includetext height=1.07) /issn /uk.co.terryburton.bwipp findresource exec

% Print header line(s)
/Courier findfont
9 scalefont
setfont

newpath
11 86 moveto
({header}) show

showpage
'''

gs_args = [
    'gs',
    '-sOutputFile={}'.format(barcode_file),
    '-dDEVICEWIDTHPOINTS=142', '-dDEVICEHEIGHTPOINTS=93',
    '-sDEVICE=pdfwrite',
    '-sDSAFER', '-sBATCH', '-sNOPAUSE', '-dQUIET',
    '-'
    ]

with subprocess.Popen(gs_args, stdin=subprocess.PIPE) as proc:
    proc.communicate(
        postscript.format(
            bwipp_location=BWIPP,
            issn_args=issn_args,
            header=header_string
            ).encode()
        )

# AppleScript InDesign to place barcode file in barcode frame
# in the active document.
# Activate InDesign.
