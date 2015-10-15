import unittest
import logging
from segment import Segment

logging.basicConfig(level=logging.WARNING)
from conf import conf

class TestSegment(unittest.TestCase):

    def test_length(self):
        a = Segment(0,0,0,100)
        b = Segment(0,0,100,0)
        c = Segment(0,0,100,200)
        self.assertEqual(a.length(), 100)
        self.assertEqual(b.length(), 100)
        self.assertAlmostEqual(c.length(), 223.606797749)

    def test_angle(self):
        a = Segment(0,0,0,100)
        b = Segment(0,0,100,0)
        c = Segment(0,0,100,100)
        self.assertEqual(a.angle(a), 0)
        self.assertEqual(b.angle(b), 0)
        self.assertEqual(a.angle(b),90)
        self.assertEqual(b.angle(a),90)
        self.assertAlmostEqual(a.angle(c), 45)

    def test_calc_lengths(self):
        s = Segment(0,0,0,100)
        s.calculate_lengths()
        self.assertEqual(s.s_spd, 0)
        self.assertEqual(s.e_spd, 0)
        self.assertEqual(len(s.get_steps()), 100/conf['plan_len'])

    def test_init_speeds(self):
        s = Segment(0,0,0,1000)
        self.assertEqual(s.s_spd, 0)
        self.assertEqual(s.e_spd, 0)

    def test_velocity_plan_minmax(self):
        # choose vals so we should get 0 start, 0 end and max in the middle
        s = Segment(0,0,0,1000)
        s.calculate_lengths()

        s.calculate_speeds()
        steps = s.get_steps()
        num_steps = len(steps)
        # middle
        self.assertEqual(steps[num_steps/2]['speed'], conf['max_spd'])
        # begin
        self.assertEqual(steps[0]['speed'], 0)
        # end
        self.assertEqual(steps[-1]['speed'], 0)

    def test_velocity_plan_nomax(self):
        # choose vals so not enough time to accelerate all the way to top speed
        s = Segment(0,0,0,110)
        s.calculate_lengths()

        s.calculate_speeds()
        steps = s.get_steps()
        num_steps = len(steps)
        # middle
        self.assertEqual(steps[num_steps/2]['speed'], conf['max_spd']/2)
        # begin
        self.assertEqual(steps[0]['speed'], 0)
        # end
        self.assertEqual(steps[-1]['speed'], 0)

    def test_velocity_plan_starthigh(self):
        # choose vals so start at half velocity and end low
        s = Segment(0,0,0,100)
        s.calculate_lengths()
        s.s_spd = conf['max_spd'] / 2

        s.calculate_speeds()
        steps = s.get_steps()
        num_steps = len(steps)
        # begin
        self.assertEqual(steps[0]['speed'], conf['max_spd']/2)
        # end
        self.assertEqual(steps[-1]['speed'], 0)

if __name__ == '__main__':
    unittest.main()


