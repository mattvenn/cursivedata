"""
needs lots of work to make this relevant again
"""
import unittest
import logging
from segment import Segment

logging.basicConfig(level=logging.WARNING)
from conf import conf

class TestMoves(unittest.TestCase):

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
        self.assertEqual(len(s.get_steps()), 100/conf['plan_len'])

    def test_init_speeds(self):
        s = Segment(0,0,0,1000)
        self.assertEqual(s.s_spd, 0)
        self.assertEqual(s.e_spd, 0)

    def test_velocity_plan_minmax(self):
        # choose vals so we should get non 0 start, 0 end and max in the middle
        s = Segment(0,0,0,1000)
        s.calculate_lengths()

        s.calculate_speeds()
        steps = s.get_steps()
        num_steps = len(steps)
        # middle
        self.assertEqual(steps[num_steps/2]['targ_spd'], conf['max_spd'])
        # begin
        self.assertNotEqual(steps[0]['targ_spd'], 0)
        # end
        self.assertEqual(steps[-1]['targ_spd'], 0)

    def test_velocity_plan_nomax(self):
        # choose vals so not enough time to accelerate all the way to top speed
        s = Segment(0,0,0,110)
        s.calculate_lengths()

        s.calculate_speeds()
        steps = s.get_steps()
        num_steps = len(steps)
        # middle
        self.assertEqual(steps[num_steps/2]['targ_spd'], conf['max_spd']/2)
        # begin
        self.assertNotEqual(steps[0]['targ_spd'], 0)
        # end
        self.assertEqual(steps[-1]['targ_spd'], 0)

    def test_velocity_plan_starthigh(self):
        # choose vals so start at half velocity and end low
        s = Segment(0,0,0,100)
        s.calculate_lengths()
        s.s_spd = conf['max_spd'] / 2

        s.calculate_speeds()
        steps = s.get_steps()
        num_steps = len(steps)
        # begin
        # speeds are at END of a step, that's why it's not exactly half speed
        self.assertAlmostEqual(steps[0]['targ_spd'], conf['max_spd']/10*(num_steps/2+1))
        # end
        self.assertEqual(steps[-1]['targ_spd'], 0)

#class TestPath(unittest.TestCase):

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



if __name__ == '__main__':
    unittest.main()


