#!/usr/bin/env python3

from datetime import datetime, timedelta

ISSN = '0307-1758'
PRICE_CODES = [None, 2, 2, 2, 2, 2, 3, None]  # Indexed to ISO weekday
PRICES = [None, None, 1.0, 1.2]  # Indexed to price codes (0 & 1 not used)


# This is shamelessly stolen from the patch for Python 3.6
# which adds ISO date specifiers %G %V and %u to strptime
def calc_julian_from_V(iso_year, iso_week, iso_weekday):
    """Calculate the Julian day based on the ISO 8601 year, week, and weekday.
    ISO weeks start on Mondays, with week 01 being the week containing 4 Jan.
    ISO week days range from 1 (Monday) to 7 (Sunday).
    """
    correction = datetime(iso_year, 1, 4).isoweekday() + 3
    ordinal = (iso_week * 7) + iso_weekday - correction
    return ordinal


# tomorrow = datetime.today() + timedelta(1)
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
ordinal = calc_julian_from_V(iso_year, iso_week, iso_day)
edition_date = datetime.strptime(
    '{y} {o:02}'.format(y=iso_year, o=ordinal),
    '%Y %j')

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

# Call Ghostscript with barcode-creating postscript
# Save barcode EPS file to new barcodes directory on server
#   (or, if server isn't available, prompt for directory)
#   Filename: 2016-WXX-SS.eps, where X is the iso week, S the sequence.
# AppleScript InDesign to place barcode file in barcode frame
# in the active document.
# Activate InDesign.

# Ghostscript command I've been using:
# gs -sOutputFile=test.eps -sDEVICE=eps2write -sDSAFER -sBATCH -sNOPAUSE test.ps
