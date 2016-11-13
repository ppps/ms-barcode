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

if __name__ == '__main__':
    unittest.main(verbosity=2)
