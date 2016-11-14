#!/usr/bin/env python3

from datetime import datetime, timedelta
from pathlib import Path
import subprocess
import sys

BWIPP = Path(__file__).resolve().parent.joinpath('bwipp', 'barcode.ps')
ISSN = '0307-1758'
PRICE_CODES = [None, 2, 2, 2, 2, 2, 3, 2]  # Indexed to ISO weekday
PRICES = [None, None, 1.0, 1.2]  # Indexed to price codes (0 & 1 not used)

barcode_folder = Path('/Users/robjwells/Desktop/')
prompt_for_folder = not barcode_folder.exists()


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


def barcode_header(date, price):
    """Format barcode header info line

    date:   datetime object
    price:  float

    barcode_header takes a datetime object and a float,
    representing the price and formats them as so:
        MSTAR YYYY-MM-DD DAY P.p

    Example:
        MSTAR 2016-11-12 SAT 1.2

    """
    template = 'MSTAR {date:%Y-%m-%d} {date:%a} {price:.1f}'
    return template.format(date=date, price=price).upper()


def barcode_filename(date, sequence):
    """Produce a name (str) matching barcode date and sequence

    date:       datetime object
    sequence:   int, where:
                    seq // 10 is the price code
                    seq % 10 is the ISO weekday

    Example output for 2016-11-14 and sequence 21:
        Barcode_2016-W46-1_21.pdf

    The format includes the ISO year, ISO week and ISO weekday
    followed by the edition sequence (a price code followed by
    the ISO weekday).

    Raises ValueError if the final digit of sequence does
    not match the ISO weekday of date.
    """
    if sequence % 10 != date.isocalendar()[2]:
        msg = 'Sequence weekday does not match date: day {day} & seq {seq}'
        msg = msg.format(day=date.isocalendar()[2], seq=sequence)
        raise ValueError(msg)
    name = 'Barcode_{d:%G}-W{d:%V}-{d:%u}_{seq}.pdf'.format(
        d=date, seq=sequence)
    return name


def date_to_sequence_and_week(date, price_codes):
    """Return sequence code and ISO week number for date

    Takes a datetime object and a list of integers representing price
    codes and returns the two-digit ISSN sequence and ISO week number.

    The sequence is a two-digit integer, where the first digit is the
    price code and the second is the ISO weekday. For example, given
    the sequence 21:
        2 is the price code
        1 is the ISO weekday

    The list of price codes should be in order such that a code's
    index in the list is equivalent to the ISO weekday - 1, ie:
        Days: [Mon, Tue, Wed, Thu, Fri, Sat, Sun]

    So given this list of price codes:
        [1, 2, 3, 4, 5, 6, 7]
    Monday has a price code of 1, through to Sunday with 7. Although
    typically the price codes will have a certain amount of consistency.

    The Morning Star's list as of 2016-11-14 looks like this:
        [2, 2, 2, 2, 2, 3, 2]
    Which has Monday-Friday as price code 2, and Saturday price code 3,
    with Sunday (which is rare) price code 2 as with the working weekdays.

    The price code list does not have to be of length 7, just long enough
    to cover the weekday for the date supplied.
    """
    _, iso_week, iso_weekday = date.isocalendar()
    sequence = price_codes[iso_weekday - 1] * 10 + iso_weekday
    return (sequence, iso_week)


if __name__ == '__main__':
    tomorrow = datetime.today() + timedelta(1)
    iso_year, iso_week, iso_day = tomorrow.isocalendar()

    # Sequence is a two-digit number: XY
    # X is the price code, Y is the ISO day of the week
    sequence = (PRICE_CODES[iso_day] * 10) + iso_day

    result = [s.strip() for s in result.decode().split(',')]
    sequence = int(result[0])
    week = int(result[1])
    if prompt_for_folder:
        barcode_folder = Path(result[2])

    # TODO: This needs to go when 3.6 is released
    edition_date = iso_to_gregorian(iso_year, week, sequence % 10)

    # TODO: Upgrade to Python 3.6 and use this version
    # edition_date = datetime.strptime(
    #    '{G}-W{V}-{u}'.format(G=iso_year, V=week, u=sequence % 10),
    #    '%G-W%V-%u'
    #    )

    header_string = barcode_header(
        date=edition_date,
        price=PRICES[sequence // 10]
        )

    issn_args = ' '.join([ISSN, str(sequence), str(week)])
    barcode_file = barcode_folder.joinpath(
        'Barcode_{0}-W{1}-{2}_{3}.pdf'.format(
            *edition_date.isocalendar(),
            sequence
            )
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
