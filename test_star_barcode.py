#!/usr/local/bin/python3

from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import unittest

import star_barcode

PROJECT_DIR = Path(__file__).resolve().parent


class TestHeader(unittest.TestCase):
    """Test barcode_header function for extra info line

    barcode_header should take a datetime object and a float,
    representing the price and format them as so:
        MSTAR YYYY-MM-DD DAY P.p
    """

    def test_header_20160104_10(self):
        """barcode_header test for Jan 1 2016 and £1 (1.0)"""
        date = datetime(2016, 1, 4)
        price = 1.0
        header = star_barcode.barcode_header(date, price)
        self.assertEqual(
            header,
            'MSTAR 2016-01-04 MON 1.0')

    def test_header_20161112_12(self):
        """barcode_header test for Nov 12 2016 and £1.20 (1.2)"""
        date = datetime(2016, 11, 12)
        price = 1.2
        header = star_barcode.barcode_header(date, price)
        self.assertEqual(
            header,
            'MSTAR 2016-11-12 SAT 1.2')


class TestFilename(unittest.TestCase):
    """Test barcode_filename function for naming barcode

    barcode_filename should take a datetime object and an int,
    representing the sequence number of the edition, and
    produce a string as so:
        Barcode_%G-W%V-%u_SS.pdf
    Where %G is the ISO year number, %V the ISO week number,
    and %u the ISO weekday number. SS is the sequence int.
    """

    def test_ordinary(self):
        """Boring test of a standard date and sequence"""
        date = datetime(2016, 11, 12)
        seq = 36
        name = star_barcode.barcode_filename(date, seq)
        self.assertEqual(
            name,
            'Barcode_2016-W45-6_36.pdf'
            )

    def test_wrong_sequence(self):
        """barcode_filename should throw when sequence is wrong

        A ValueError exception should be raised if the second digit
        of the sequence (sequence % 10) is not the same as the ISO
        weekday number (%u).
        """
        date = datetime(2016, 11, 12)
        seq = 31
        with self.assertRaises(ValueError):
            star_barcode.barcode_filename(date, seq)

    def test_year_boundary(self):
        """barcode_filename should use ISO week year not standard year

        January 1 2017 is the final ISO day (Sunday) in the final ISO
        week of 2016 (52), so the fileame should be:
            Barcode_2016-W52-7-SS.pdf
        """
        date = datetime(2017, 1, 1)
        seq = 27
        name = star_barcode.barcode_filename(date, seq)
        self.assertEqual(
            name,
            'Barcode_2016-W52-7_27.pdf'
            )

    def test_price_code_0(self):
        """barcode_filename should accept sequences 01-07

        Sequences 01-07 are all represented by single-digit integers,
        and should be properly zero-padded in the filename.

        The range allowed here is deliberately shorter than elsewhere
        in the program because barcode_filename is designed to work
        only with a corresponding date, and ISO weekdays run 1-7.
        Special-case sequences 00, 98 and 99 are not considered here.
        """
        start_date = datetime(2016, 11, 13)  # Note this is a Sunday, and
                                       # must have timedelta added
        for x in range(1, 7):
            with self.subTest(x=x):
                date = start_date + timedelta(x)
                result = star_barcode.barcode_filename(date, x)
                self.assertEqual(
                    result.split('.')[0][-2:],
                    '{0:02}'.format(x)
                    )


class TestDateToSequenceWeek(unittest.TestCase):
    """Test date_to_sequence_and_week

    date_to_sequence_and_week takes a datetime object and a list of
    integers representing price codes and returns the two-digit
    ISSN sequence and ISO week number.

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

    It shouldn't be a requirement that the list is always length 7, just
    that it covers the publication weekdays.

    The sequence returned is an integer 1-7 … 91-97 for simplicity.
    When used, the sequence should be zero-padded to length 2
    (but this is up to other functions).

    As used, the sequence is a two-digit number, where the first digit is
    the price code and the second is the ISO weekday. For example, given
    the sequence 21:
        2 is the price code
        1 is the ISO weekday

    While sequences 0, 8, 9 … 90, 98, 99 are valid, they are not returned
    by this function as it operates on dates, for which ISO weekdays run
    1-7 for Monday-Sunday.
    """

    def test_standard_seq_week(self):
        """date_to_sequence_and_week handles a typical case

        Given a datetime object for 2016-11-15 (a Tuesday)
        and a 7-long list of the integer 2 the sequence
        returned should be 22 and the week 46.
        """
        date = datetime(2016, 11, 15)
        prices = [2] * 7
        expected_sequence = 22
        expected_week = 46
        self.assertEqual(
            star_barcode.date_to_sequence_and_week(
                date=date, price_codes=prices),
            (expected_sequence, expected_week)
            )

    def test_short_prices(self):
        """date_to_sequence_and_week handles a short price code list

        Given a datetime object for 2016-11-15 (a Tuesday)
        and a 2-long list of the integer 2 the sequence
        returned should be 22 and the week 46."""
        date = datetime(2016, 11, 15)
        prices = [2] * 2
        expected_sequence = 22
        expected_week = 46
        self.assertEqual(
            star_barcode.date_to_sequence_and_week(
                date=date, price_codes=prices),
            (expected_sequence, expected_week)
            )

    def test_gregorian_mismatch(self):
        """date_to_sequence_and_week correctly uses the ISO week

        Given a date that has a different week number under the typical
        Gregorian system and the ISO system, date_to_sequence_and_week
        should return the ISO week.

        January 1 2017 has the ISO calendar week 2016-W52-7,
        but the Gregorian week 2017-W00.
        """
        date = datetime(2017, 1, 1)
        prices = [2] * 7
        expected_sequence = 27
        expected_week = 52
        self.assertEqual(
            star_barcode.date_to_sequence_and_week(
                date=date, price_codes=prices),
            (expected_sequence, expected_week)
            )

    def test_incrementing_codes(self):
        """date_to_sequence_and_week correctly uses price code list

        Given a price code list that increments by 1 each day (in line
        with the ISO weekday number), date_to_sequence_and_week should
        return corresponding sequences (11, 22, 33 … 77)
        """
        date = datetime(2016, 11, 14)
        prices = list(range(1, 8))
        week = 46
        for i in range(7):
            with self.subTest(i=i):
                self.assertEqual(
                    star_barcode.date_to_sequence_and_week(
                        date + timedelta(i), prices),
                    ((i + 1) * 11, week)
                    )


class TestPostscript(unittest.TestCase):
    """Test the formatting of the Postscript commands"""
    def setUp(self):
        self.bwipp = PROJECT_DIR.joinpath('bwipp', 'barcode.ps')
        self.issn = '0307-1758'

    def test_typical(self):
        """construct_postscript correctly formats typical arguments"""
        seq = 21
        week = 46
        header = 'MSTAR 2016-11-14 MON 1.0'
        issn_args = ' '.join([self.issn, str(seq), str(week)])
        result = star_barcode.construct_postscript(
            bwipp_location=self.bwipp,
            issn=self.issn,
            sequence=seq,
            week=week,
            header_line=header
            )
        self.assertGreater(result.find(str(self.bwipp)), -1)
        self.assertGreater(result.find(issn_args), -1)
        self.assertGreater(result.find(header), -1)

    def test_missing_bwipp(self):
        """construct_postscript raises ValueError if bwipp is missing

        If the location passed to construct_postscript for the location
        of the bwipp postscript library does not exist, then it should
        raise ValueError.
        """
        seq = 21
        week = 46
        header = 'MSTAR 2016-11-14 MON 1.0'
        with self.assertRaisesRegex(ValueError, 'BWIPP'):
            star_barcode.construct_postscript(
                bwipp_location=Path('/fake-path/not-here.ps'),
                issn=self.issn,
                sequence=seq,
                week=week,
                header_line=header
                )

    def test_issn_incorrect_length(self):
        """construct_postscript raises ValueError for ISSN of incorrect length

        ISSNs are either 7 or 8 digits long (8 being the optional check
        digit), with a mandatory (for BWIPP) hyphen in the fifth place.

        construct_postscript should raise a ValueError if the ISSN is
        not of the form \d{4}-\d{3,4}.
        """
        issns = ['0307-15', '0307-15789', '03071758', '0307175']
        for num in issns:
            with self.subTest(num=num):
                with self.assertRaisesRegex(ValueError, num):
                    star_barcode.construct_postscript(
                        issn=num,
                        bwipp_location=self.bwipp,
                        sequence=21,
                        week=46,
                        header_line=''
                        )

    def test_sequence_outside_range(self):
        """construct_postscript raises ValueError if sequence outside range

        Sequence can be between 00 and 99. Although in our usage the
        second digit is the ISO weekday, so in practice limited 01-07 and
        91-97, special sequences may require the extra numbers.

        Must not raise for sequences 00-09, represented by integers 0-9,
        as these are valid sequences (and should be padded as such),
        tested separately.
        """
        seqs = [-1, 100]
        for seq in seqs:
            with self.subTest(seq=seq):
                with self.assertRaisesRegex(ValueError, str(seq)):
                    star_barcode.construct_postscript(
                        sequence=seq,
                        bwipp_location=self.bwipp,
                        issn=self.issn,
                        week=46,
                        header_line=''
                        )

    def test_sequence_0_to_9(self):
        """construct_postscript must not raise for sequences 00-09

        As all possible sequences run 00-99, they can be adequately
        represented by an integer rather than a string. But the
        construct_postscript function must not raise for integers
        0-9, even though as (unformatted) strings they are of length 1.
        """
        seqs = list(range(10))
        for seq in seqs:
            with self.subTest(seq=seq):
                result = star_barcode.construct_postscript(
                    sequence=seq,
                    bwipp_location=self.bwipp,
                    issn=self.issn,
                    week=20,
                    header_line=''
                    )
                self.assertGreater(
                    result.find('{0} {1:02}'.format(self.issn, seq)),
                    -1
                    )

    def test_sequence_specials(self):
        """construct_postscript must not raise for special sequences

        While the paper only uses sequences 01-07 through 91-97, the
        missing numbers are valid (00, 08, 09 … 90, 98, 99) and should
        be accepted by construct_postscript.
        """
        special_digits = [0, 8, 9]
        for t in range(0, 10):
            for special in special_digits:
                seq = t * 10 + special
            with self.subTest(seq=seq):
                result = star_barcode.construct_postscript(
                    sequence=seq,
                    bwipp_location=self.bwipp,
                    issn=self.issn,
                    week=20,
                    header_line=''
                    )
                self.assertGreater(
                    result.find('{0} {1:02}'.format(self.issn, seq)),
                    -1
                    )


    def test_week_wrong(self):
        """construct_postscript raises ValueError if 0 < week < 54

        ISO weeks must be between 1 and 53.
        """
        weeks = [0, 54]
        for week in weeks:
            with self.subTest(week=week):
                with self.assertRaisesRegex(ValueError, str(week)):
                    star_barcode.construct_postscript(
                        week=week,
                        bwipp_location=self.bwipp,
                        issn=self.issn,
                        sequence=21,
                        header_line=''
                        )

    def test_week_in_range(self):
        """construct_postscript accepts week >= 1, <= 53"""
        weeks = list(range(1, 54))
        seq = 21
        for week in weeks:
            with self.subTest(week=week):
                result = star_barcode.construct_postscript(
                    week=week,
                    bwipp_location=self.bwipp,
                    issn=self.issn,
                    sequence=seq,
                    header_line=''
                    )
                self.assertGreater(
                    result.find('{0} {1:02} {2:02}'.format(
                        self.issn, seq, week)),
                    -1
                    )

class TestCreateBarcode(unittest.TestCase):
    """Test create_barcode function, which calls ghostscript to make file"""
    def setUp(self):
        self.postscript = '''\
%!PS
(bwipp/barcode.ps) run

11 5 moveto (0307-1758 25 45) (includetext height=1.07) /issn /uk.co.terryburton.bwipp findresource exec

% Print header line(s)
/Courier findfont
9 scalefont
setfont

newpath
11 86 moveto
(MSTAR 2016-11-11 FRI 1.0) show

showpage
'''

    def test_typical(self):
        """Call create_barcode with typical values"""
        with tempfile.TemporaryDirectory() as tempdir:
            filename = 'test-barcode.pdf'
            file_path = Path(tempdir, filename)

            # Make sure it's not there by accident
            self.assertFalse(file_path.exists())

            star_barcode.create_barcode(
                postscript=self.postscript,
                output_file=file_path)

            self.assertTrue(file_path.exists())


class TestProcessArguments(unittest.TestCase):
    """Test process_arguments function

    process_arguments turns arguments returned by docopt into
    the appropriate types for other functions to use.
    """

    def test_date_only(self):
        """process_arguments turns date into datetime"""
        args = {
            '--directory': './',
            '<date>': '2016-11-15',
            '<header>': None,
            '<seq>': None,
            '<week>': None
            }
        expected = {
            '--directory': Path('./'),
            '<date>': datetime(2016, 11, 15),
            '<header>': None,
            '<seq>': None,
            '<week>': None
            }
        self.assertEqual(
            star_barcode.process_arguments(args),
            expected
            )

    def test_seq_week_header(self):
        """process_arguments turns date into datetime"""
        args = {
            '--directory': './',
            '<date>': None,
            '<header>': 'Header line',
            '<seq>': '22',
            '<week>': '46'
            }
        expected = {
            '--directory': Path('./'),
            '<date>': None,
            '<header>': 'Header line',
            '<seq>': 22,
            '<week>': 46
            }
        self.assertEqual(
            star_barcode.process_arguments(args),
            expected
            )


if __name__ == '__main__':
    unittest.main(verbosity=2)
