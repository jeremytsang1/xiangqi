import unittest
import Stack as xg


class StackTest(unittest.TestCase):
    def test_init(self):
        stack = xg.Stack()
        self.assertEqual(0, stack.get_size())
        self.assertEqual(None, stack.peek())
        self.assertTrue(stack.is_empty())
