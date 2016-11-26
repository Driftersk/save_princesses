import unittest

from main import Node


class NodeTests(unittest.TestCase):
    def test_node_constructor(self):
        value = 'A'
        x = 1
        y = 5
        node = Node(value, x, y)
        self.assertEqual((node.value, node.x, node.y), (value, x, y))

    def test_node_equation(self):
        value = 'F'
        x = 5
        y = 6
        node1 = Node(value, x, y)
        node2 = Node('F', 5, 6)
        self.assertEqual(node1, node2)
