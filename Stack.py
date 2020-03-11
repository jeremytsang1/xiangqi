class Node:
    """Defines a simple Node class with public data and link to other objects of
       type Node.
    """
    def __init__(self, data):
        """Creates an object of type Node with given data and link.

        Parameters
        ----------
        data: int
            Value of data for Node to hold.
        next_node: Node
            Link to access another object of type Node.
        """
        self._data = data
        self._next = None

    def get_data(self):
        return self._data

    def get_next(self):
        return self._next
