import unittest
from planner import Path

conf = {
    'plan_len' : 25,    # cm
    'max_spd' : 20.0,
    'min_spd' : 1.0,
    'spd_err' : 0.0,  # % error in speed measurement of servo
    'acc' : 0.1,
    'len_err' : 0,   # random length err up to this in cm
    'width' : 700,
    'height' : 500,
    'scaling' : 8, # how much bigger to make the png than the robot
}

class TestPath(unittest.TestCase):
    
    def test_add(self):
        p = Path()
        self.assertFalse(p.is_finished())
        s = Segment(conf,0,0,0,100)
        p.add_segment(s)
        self.assertFalse(p.is_finished())
        s = Segment(conf,0,100,0,200)
        p.add_segment(s)
        self.assertFalse(p.is_finished())
        s = Segment(conf,0,200,0,0)
        p.add_segment(s)
        self.assertTrue(p.is_finished())


if __name__ == '__main__':
    unittest.main()

