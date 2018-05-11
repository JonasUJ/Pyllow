import unittest
from src.Stream import Stream


STREAM_ITEMS = 'A', 'B', 'C'


class StreamTest(unittest.TestCase):

    def setUp(self):
        self.stream = Stream(STREAM_ITEMS)

    def tearDown(self):
        del self.stream

    def test_current(self):
        self.assertIsNone(self.stream.current)
        self.stream._i = 0
        self.assertEqual(self.stream.current, 'A')

    def test_is_not_finished(self):
        self.assertTrue(self.stream.is_not_finished)
        self.stream._i = 2
        self.assertFalse(self.stream.is_not_finished)

    def test_next(self):
        self.assertEqual(self.stream.next(), 'A')
        self.assertEqual(self.stream.next(), 'B')
        self.assertEqual(self.stream.next(), 'C')
        self.assertIsNone(self.stream.next())

    def test_prev(self):
        self.stream._i = 3
        self.assertEqual(self.stream.prev(), 'C')
        self.assertEqual(self.stream.prev(2), 'A')
        self.assertIsNone(self.stream.prev())

    def test_peek_next(self):
        self.assertEqual(self.stream.peek_next(), 'A')
        self.stream._i = 1
        self.assertEqual(self.stream.peek_next(), 'C')
        self.stream._i = 2
        self.assertIsNone(self.stream.peek_next())

    def test_peek_prev(self):
        self.stream._i = 3
        self.assertEqual(self.stream.peek_prev(), 'C')
        self.assertEqual(self.stream.peek_prev(2), 'B')
        self.assertEqual(self.stream.peek_prev(3), 'A')
        self.assertIsNone(self.stream.peek_prev(4))

    def test_skip(self):
        self.assertEqual(self.stream.skip(1), 'A')
        self.assertEqual(self.stream.skip(2), 'C')
        self.assertEqual(self.stream.skip(-1), 'B')
        self.assertIsNone(self.stream.skip(2))

    def test_getitem(self):
        self.assertEqual(self.stream[0], 'A')
        self.assertEqual(self.stream[1], 'B')
        self.assertEqual(self.stream[2], 'C')
        

if __name__ == '__main__':
    unittest.main()
