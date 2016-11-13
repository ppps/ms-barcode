#!/usr/local/bin/python3

from datetime import datetime
import unittest

import star_barcode


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


if __name__ == '__main__':
    unittest.main(verbosity=2)
