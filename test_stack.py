import unittest
import Stack as xg


class StackTest(unittest.TestCase):
    def test_init(self):
        stack = xg.Stack()
        self.assertEqual(0, stack.get_size())
        self.assertEqual(None, stack.peek())
        self.assertTrue(stack.is_empty())
        self.assertEqual(None, stack.pop())

    def test_peek_push_from_empty(self):
        test_cases = {
            (2,): 2,
            (2, 5): 5,
            (2, 5, 3): 3,
            (2, 2, 2, 2): 2,
        }
        for params, top in test_cases.items():
            stack = xg.Stack()
            for param in params:
                stack.push(param)
            self.assertEqual(top, stack.peek())
