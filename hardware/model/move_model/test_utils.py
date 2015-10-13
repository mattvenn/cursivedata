import unittest
from planner import Segment
from planner import Path

class TestPath(unittest.TestCase):
    
    def test_add(self):
        p = Path()
        self.assertFalse(p.is_finished())
        s = Segment(0,0,0,100)
        p.add_segment(s)
        self.assertFalse(p.is_finished())
        s = Segment(0,100,0,200)
        p.add_segment(s)
        self.assertFalse(p.is_finished())
        s = Segment(0,200,0,0)
        p.add_segment(s)
        self.assertTrue(p.is_finished())

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

if __name__ == '__main__':
    unittest.main()

