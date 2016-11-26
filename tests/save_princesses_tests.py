import unittest

from main import save_princess, get_trace_distance, Node


class SavePrincessesTests(unittest.TestCase):
    def test_one_liner_with_one_princess(self):
        terrain = [
            "CDCP"
        ]
        path = save_princess(terrain, 10)
        expected = [Node('C', 0, 0),
                    Node('D', 1, 0),
                    Node('C', 2, 0),
                    Node('P', 3, 0),
                    ]
        self.assertEqual(path, expected)

    def test_one_liner_with_two_princess(self):
        terrain = [
            "CDCPHHP"
        ]
        path = save_princess(terrain, 10)
        expected = [Node('C', 0, 0),
                    Node('D', 1, 0),
                    Node('C', 2, 0),
                    Node('P', 3, 0),
                    Node('H', 4, 0),
                    Node('H', 5, 0),
                    Node('P', 6, 0),
                    ]
        self.assertEqual(path, expected)

    def test_one_princess(self):
        terrain = [
            "CDCH",
            "CNNP"
        ]
        path = save_princess(terrain, 10)
        expected = [Node('C', 0, 0),
                    Node('D', 1, 0),
                    Node('C', 2, 0),
                    Node('H', 3, 0),
                    Node('P', 3, 1),
                    ]
        self.assertEqual(path, expected)

    def test_two_princess(self):
        terrain = [
            "CDPH",
            "CNNP"
        ]
        path = save_princess(terrain, 10)
        expected = [Node('C', 0, 0),
                    Node('D', 1, 0),
                    Node('P', 2, 0),
                    Node('H', 3, 0),
                    Node('P', 3, 1),
                    ]
        self.assertEqual(path, expected)

    def test_tree_princess(self):
        terrain = [
            "CHCP",
            "CNPN",
            "DNHP"
        ]
        path = save_princess(terrain, 10)
        expected = [Node('C', 0, 0),
                    Node('C', 0, 1),
                    Node('D', 0, 2),
                    Node('C', 0, 1),
                    Node('C', 0, 0),
                    Node('H', 1, 0),
                    Node('C', 2, 0),
                    Node('P', 3, 0),
                    Node('C', 2, 0),
                    Node('P', 2, 1),
                    Node('H', 2, 2),
                    Node('P', 3, 2),
                    ]
        self.assertEqual(path, expected)

    def test_pass(self):
        self.assertTrue(True)

    def test_fail(self):
        self.assertFalse(False)

if __name__ == '__main__':
    unittest.main()
