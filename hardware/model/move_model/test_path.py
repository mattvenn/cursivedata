import unittest
import logging
from ppath import Moves
import math

logging.basicConfig(level=logging.WARNING)
from conf import conf

class TestPath(unittest.TestCase):

    def test_calc_radius(self):
        m = Moves()
        m.add_point(2,1.5)
        m.add_point(6,4.5)
        m.add_point(11.75,6.25)
        self.assertAlmostEqual(m.calc_rad(1), 15.89900293006253)

        m = Moves()
        m.add_point(2,0)
        m.add_point(0,2)
        m.add_point(-2,0)
        self.assertAlmostEqual(m.calc_rad(1), 2)

    def test_calc_len(self):
        m = Moves()
        m.add_point(0,0)
        m.add_point(2,2)
        self.assertAlmostEqual(m.calc_len(1), math.sqrt(8))

        m = Moves()
        m.add_point(0,0)
        m.add_point(2,0)
        self.assertAlmostEqual(m.calc_len(1), 2)

if __name__ == '__main__':
    unittest.main()


