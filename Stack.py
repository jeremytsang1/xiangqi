class Stack:
    """
    An implementation of the Stack ADT that uses Python's built-in lists.

    Taken from CS 162, "Exploration: Linked lists, stacks, queues".
    """
    def __init__(self):
        self._list = []

    def get_size(self):
        return len(self._list)

    def peek(self):
        if self.get_size() == 0:
            return None
        return self._list[-1]

    def is_empty(self):
        return len(self._list) == 0

    def push(self, data):
        self._list.append(data)

    def pop(self):
        if self.is_empty():
            return None

        val = self._list[-1]
        del self._list[-1]
        return val
