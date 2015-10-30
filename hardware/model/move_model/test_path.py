import unittest
import logging
from ppath import Moves
import math

logging.basicConfig(level=logging.DEBUG)
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

    def test_split_move(self):
        m = Moves()
        m.add_point(0,0)
        m.add_point(100,0)

        conf['plan_len'] = 10
        m.break_segments()
        self.assertEqual(len(m.broken_points), 11)
    
    def test_calc_max_vel(self):
        m = Moves()
        m.add_point(0,0)
        m.add_point(100,0)

        conf['plan_len'] = 10
        m.break_segments()
        self.assertEqual(len(m.broken_points), 11)

        m.calc_max_velocity()
        self.assertEqual(m.broken_points[0]['max_spd'], 0)
        self.assertEqual(m.broken_points[10]['max_spd'], 0)
        for i in range(1,10):
            self.assertEqual(m.broken_points[i]['max_spd'], conf['max_spd'])

    def test_plan_vel(self):
        m = Moves()
        m.add_point(0,0)
        m.add_point(100,0)

        conf['plan_len'] = 10
        m.break_segments()
        m.calc_max_velocity()
        m.plan_velocity()
        m.dump()



if __name__ == '__main__':
    unittest.main()


