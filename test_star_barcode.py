#!/usr/local/bin/python3

from datetime import datetime, timedelta
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

    The sequence is a two-digit integer, where the first digit is the
    price code and the second is the ISO weekday. For example, given
    the sequence 21:
        2 is the price code
        1 is the ISO weekday
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


if __name__ == '__main__':
    unittest.main(verbosity=2)
