import unittest

import sys

from main import shortest_path_all, TerrainGraph, Node


class Tests(unittest.TestCase):
    def setUp(self):
        pass

    def test_simple_graph(self):
        terrain = [
            "CN",
            "CC"
        ]
        g = TerrainGraph(terrain)
        source = g.get_node(0, 0)
        destinations = {g.get_node(1, 1)}
        paths = shortest_path_all(source, destinations, g, False)

        expected = {}
        self.add_to_expected(expected, g, [(0, 0), (0, 1), (1, 1)], 2, False)

        self.assertEqual(expected, paths)

    def test_4x4_graph(self):
        terrain = [
            "CNHC",
            "CHNC",
            "DNNH",
            "CPCC"
        ]
        g = TerrainGraph(terrain)
        source = g.get_node(0, 0)
        destinations = {g.get_node(1, 3), g.get_node(3, 0)}
        paths = shortest_path_all(source, destinations, g, False)

        expected = {}
        self.add_to_expected(expected, g, [(0, 0), (0, 1), (0, 2), (0, 3), (1, 3)], 4, False)
        self.add_to_expected(expected, g, [(0, 0), (0, 1), (0, 2), (0, 3), (1, 3), (2, 3), (3, 3), (3, 2), (3, 1),
                                           (3, 0)], 10, False)

        self.assertEqual(expected, paths)

    def test_unreachable(self):
        terrain = [
            "CN",
            "NC"
        ]
        g = TerrainGraph(terrain)
        source = g.get_node(0, 0)
        destinations = {g.get_node(1, 1)}
        paths = shortest_path_all(source, destinations, g, False)

        expected = {g.get_node(1, 1): ([], sys.maxsize, False)}

        self.assertEqual(expected, paths)

    def construct_expected_path(self, graph, coords):
        expected_path = []
        for coord in coords:
            expected_path.append(graph.get_node(coord[0], coord[1]))
        return expected_path

    def add_to_expected(self, expected, graph, coords, distance, teleports_activated):
        """
        Wrapper around return dictionary from shortest_path_all function
        :param expected:
        :param graph:
        :param coords:  cannot be empty []
        :param distance:
        :param teleports_activated:
        :return:
        """
        destination = graph.get_node(coords[-1][0], coords[-1][1])
        path = self.construct_expected_path(graph, coords)
        expected[destination] = (path, distance, teleports_activated)
