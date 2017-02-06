#!/usr/bin/env python3
"""Star Barcode

Usage:
  star_barcode.py (<date> | <seq> <week> <header>) [--directory=<dir>]

Options:
  -d <dir>, --directory=<dir>  Where to save the barcode [default: ./]
  -h, --help                   Display this message
  --version                    Display version

"""


from datetime import datetime
from pathlib import Path
import re
import subprocess
import sys

from docopt import docopt

BWIPP = Path(__file__).resolve().parent.joinpath('bwipp', 'barcode.ps')
ISSN = '0307-1758'
PRICE_CODES = [2, 2, 2, 2, 2, 3, 2]
PRICES = [None, None, 1.0, 1.2]  # Indexed to price codes (0 & 1 not used)


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
    name = 'Barcode_{d:%G}-W{d:%V}-{d:%u}_{seq:02}.pdf'.format(
        d=date, seq=sequence)
    return name


def date_to_sequence_and_week(date, price_codes):
    """Return sequence code and ISO week number for date

    Takes a datetime object and a list of integers representing price
    codes and returns the ISSN sequence and ISO week number as integers.


    The sequence is an integer 1-7 … 91-97, where the tens position is
    the price code and the units position the ISO weekday. Sequences
    that run 1-7 have a price code of 0.

    For example, given the sequence 21:
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


def construct_postscript(*, bwipp_location, issn, sequence, week, header_line):
    """Format a Postscript script ready for passing to ghostscript

    bwipp_location:  pathlib.Path object for the BWIPP Postscript library
    issn:            ISSN number, str matching regex \d{4}-\d{3,4}
    sequence:        2-digit int, usually price code & ISO weekday
    week:            ISO week number, as int
    header_line:     str up to length 24, extra info printed above barcode
    """
    postscript = '''\
%!PS
({bwipp_location}) run

11 5 moveto ({issn} {seq:02} {week:02}) (includetext height=1.07) /issn /uk.co.terryburton.bwipp findresource exec

% Print header line(s)
/Courier findfont
9 scalefont
setfont

newpath
11 86 moveto
({header}) show

showpage
'''
    if not bwipp_location.exists():
        raise ValueError('BWIPP location is incorrect')
    else:
        bwipp_location = bwipp_location.resolve()

    if not re.match(r'^\d{4}-\d{3,4}$', issn):
        raise ValueError('ISSN {0} is in incorrect format'.format(issn))

    if not 0 <= sequence <= 99:
        raise ValueError(
            'Sequence {0} is outside of range 0-99'.format(sequence))

    if not 0 < week < 54:
        raise ValueError(
            'Week {0} is not a valid ISO week. Must be between 1 and 53'
            .format(week))

    return postscript.format(
        bwipp_location=bwipp_location,
        issn=issn,
        seq=sequence,
        week=week,
        header=header_line)


def create_barcode(postscript, output_file):
    """Save barcode file to output_file from postscript

    postscript:     str, a formatted PostScript script

    output_file:    pathlib.Path or str

    output_file is formatted into a str, so can be any class that
    produces a Unix path on str().

    Calls ghostscript behind the scenes using subprocess.
    """
    gs_args = [
        'gs',
        '-sOutputFile={}'.format(output_file),
        '-dDEVICEWIDTHPOINTS=142', '-dDEVICEHEIGHTPOINTS=93',
        '-sDEVICE=pdfwrite',
        '-dPDFX',
        '-sDSAFER', '-sBATCH', '-sNOPAUSE', '-dQUIET',
        '-'
        ]
    subprocess.run(args=gs_args, input=postscript.encode('utf-8'))


def process_arguments(arguments):
    """Return arguments dict with types converted"""
    if arguments['<date>'] is not None:
        arguments['<date>'] = datetime.strptime(arguments['<date>'],
                                                '%Y-%m-%d')

    arguments['--directory'] = Path(arguments['--directory']).expanduser()

    for key in ['<seq>', '<week>']:
        if arguments[key] is not None:
            arguments[key] = int(arguments[key])

    return arguments


def barcode_from_date(date, output_dir=None):
    """Create a barcode from date and save to output_dir

    Convenience wrapper around main.
    """
    barcode_args = [date.strftime('%Y-%m-%d')]
    if output_dir is not None:
        barcode_args.append('--directory=' + str(output_dir))
    return main(cli_args=barcode_args)


def barcode_from_details(sequence, week, header, output_dir=None):
    """Create a barcode by specifying the details directly

    Convenience wrapper around main.
    """
    barcode_args = [sequence, week, header]
    if output_dir is not None:
        barcode_args.append('--directory=' + str(output_dir))
    return main(cli_args=barcode_args)


def main(cli_args=sys.argv[1:]):
    """Create barcode from command line args and return path to file"""
    arguments = docopt(
        doc=__doc__, argv=cli_args, version='Star Barcode 0.1.0')
    arguments = process_arguments(arguments)

    if arguments['<date>'] is not None:
        date = arguments['<date>']
        seq, week = date_to_sequence_and_week(
            date=date, price_codes=PRICE_CODES)
        header = barcode_header(
            date=date, price=PRICES[seq // 10])
        filename = barcode_filename(date=date, sequence=seq)
    else:
        seq = arguments['<seq>']
        week = arguments['<week>']
        header = arguments['<header>'].upper()
        filename = 'Barcode_SPECIAL_W{w:02}_{s:02}.pdf'.format(s=seq, w=week)

    path = arguments['--directory'].joinpath(filename)

    postscript = construct_postscript(
        bwipp_location=BWIPP,
        issn=ISSN,
        sequence=seq,
        week=week,
        header_line=header)

    create_barcode(postscript=postscript, output_file=path)
    return path.resolve()


if __name__ == '__main__':
    print(main())
