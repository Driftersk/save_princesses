#! python3

import sys
import heapq
from functools import total_ordering, reduce

import itertools

"""
Symbol: cost, description
C: 1, path
H: 2, forrest
N: sys.maxsize, cliff
D: 1, dragon
P: 1, princess
0-9: 0, teleport to all places with same number
G: 1, turns on ability to teleport

Player starts at [0,0], needs to find dragon before t turns, and
get to all princesses in shortest time.
"""


@total_ordering
class Node:
    def __init__(self, value, x, y):
        self.value = value
        self.x = x
        self.y = y

    def __str__(self):
        return 'Node({} ,x: {},y: {})'.format(self.value, self.x, self.y)

    @staticmethod
    def _is_valid_operand(other):
        return hasattr(other, 'value') and hasattr(other, 'x') and hasattr(other, 'y')

    def __eq__(self, other):
        if not self._is_valid_operand(other):
            return NotImplemented
        return (self.value, self.x, self.y) == (other.value, other.x, other.y)

    def __lt__(self, other):
        if not self._is_valid_operand(other):
            return NotImplemented
        return (self.x, self.y, self.value) < (other.x, other.y, other.value)

    def __hash__(self, *args, **kwargs):
        return super().__hash__(*args, **kwargs)


class TerrainGraph:
    FOOT_DISTANCE = {'C': 1, 'H': 2, 'N': sys.maxsize, 'D': 1, 'P': 1, '0': 1, '1': 1, '2': 1, '3': 1, '4': 1, '5': 1,
                     '6': 1, '7': 1, '8': 1, '9': 1, 'G': 1}
    TELEPORT_DISTANCE = {chr(symbol): 0 for symbol in range(ord('0'), ord('9') + 1)}

    def __init__(self, terrain):
        height = len(terrain)
        if height == 0:
            raise ValueError('Map must be size at least 1x1.')
        width = len(terrain[0])
        if width == 0:
            raise ValueError('Map must be size at least 1x1.')

        self.nodes = {}             # {(x, y): Node(...), ...}     fast access to Node in x,y coord
        self.edges = {}             # {Node(...): {Node(...): x, ...}}     fast access to neighbours of Node
        self.teleports = {}         # {Node1(...): {Node2(...), ...}}     instant teleport from Node to Node2
        self.dragon = None          # Node(...)      Node where value is 'D' (can be only one)
        self.princesses = set()     # set(Node(...))    Nodes where value is 'P'

        teleports_coords = [[] for _ in range(10)]  # [[(x,y),...],...}     temporary, coordinates for teleports
        for y, line in enumerate(terrain):
            for x, symbol in enumerate(line):
                node = Node(symbol, x, y)
                self.nodes[(x, y)] = node
                self.edges[node] = {}

                if ord('0') <= ord(symbol) <= ord('9'):
                    teleports_coords[int(symbol)].append(node)

                if symbol == 'D':
                    self.dragon = node
                elif symbol == 'P':
                    self.princesses.add(node)

        # connect basic paths
        for node in self.nodes.values():
            cost = self.FOOT_DISTANCE.get(node.value)
            if cost == sys.maxsize:     # cannot traverse
                continue

            # top
            top = self.get_node(node.x, node.y-1)
            if top:
                self.edges[node][top] = cost
            # bottom
            bottom = self.get_node(node.x, node.y+1)
            if bottom:
                self.edges[node][bottom] = cost
            # left
            left = self.get_node(node.x-1, node.y)
            if left:
                self.edges[node][left] = cost
            # right
            right = self.get_node(node.x+1, node.y)
            if right:
                self.edges[node][right] = cost

        # connect teleports
        for teleport_num in range(len(teleports_coords)):   # for each teleport number
            for node in teleports_coords[teleport_num]:     # for each node in teleport number set
                self.teleports[node] = set()    # add teleport as key
                for t in teleports_coords[teleport_num]:    # add other teleports from set
                    if node != t:
                        self.teleports[node].add(t)

    def get_node(self, x, y) -> Node:
        return self.nodes.get((x, y), None)

    def get_neighbours(self, node, teleports_activated=False):
        neighbours = self.edges.get(node)
        if teleports_activated and self.teleports.get(node):
            for teleport_exist in self.teleports.get(node):         # get all teleport exits
                cost = self.TELEPORT_DISTANCE[node.value]
                # check if teleport route is faster then by walking, (in case 0 its always faster)
                if teleport_exist not in neighbours.keys() or cost < neighbours.get(teleport_exist):
                    neighbours[teleport_exist] = cost   # add possible teleport exit with set cost by distance
        return neighbours

    def get_distance_to_neighbour(self, source, neighbour, teleports_activated=False):
        direct = self.edges.get(source).get(neighbour, sys.maxsize)
        teleport = self.TELEPORT_DISTANCE.get(source.value) \
            if teleports_activated and neighbour in self.teleports.get(source) else sys.maxsize
        return min(direct, teleport)

    def __str__(self):
        nodes = "{"
        for coords, node in self.nodes.items():
            nodes += str(node) + ", "
        nodes = nodes[:-2] + "}"

        edges = "{\n"
        for src, dsts in self.edges.items():
            edges += "\t" + str(src) + ": {"
            for node, cost in dsts.items():
                edges += "\n\t\t" + str(node) + ": " + str(cost) + ","
            edges += "\n\t},\n"
        edges += "}"

        teleports = "{\n"
        for src, dsts in self.teleports.items():
            teleports += "\t" + str(src) + ": {"
            for node in dsts:
                teleports += "\n\t\t" + str(node) + ": " + str(self.TELEPORT_DISTANCE.get(node.value)) + ","
            teleports += "\n\t},\n"
        teleports += "}"

        return "Terrain graph:\nNodes: " + nodes + "\nNormal edges: " + edges + "\nTeleports: " + teleports


def shortest_path_any(start, end_nodes, graph, teleports_activated=False):
    def change_distance(q, u, d):
        """
        :param q: priority queue
        :param u: vertex
        :param d: new distance
        """
        for i, node in enumerate(q):
            if node[1] == u:
                q[i] = (d, node[1])
                break
        heapq.heapify(q)

    teleport_trace = None

    gpt = get_predecesors_trace     # just alias for that long function name

    # {Node(...): x, ...}       where x is distance from start node to Node
    shortest_distances = {node: sys.maxsize for node in graph.nodes.values()}
    shortest_distances[start] = 0       # where we start, its distance 0
    predecessors = {}       # {Node1(...): Node2(...), ...}         where Node1 is child of Node2

    # priority queue
    calculated_distances = [(0, node) if node == start else (sys.maxsize, node) for node in graph.nodes.values()]
    heapq.heapify(calculated_distances)

    done = set()       # nodes which already have shortest path calculated

    while calculated_distances:
        distance, cun = heapq.heappop(calculated_distances)        # cun = closest unprocessed node
        done.add(cun)
        neighbours = graph.get_neighbours(cun, teleports_activated)
        for neighbour in neighbours:
            if neighbour not in done:
                current_distance = shortest_distances.get(cun) + graph.get_distance_to_neighbour(cun, neighbour)
                if current_distance < shortest_distances.get(neighbour):
                    # chance distance of neighbour to distance of cun + distance from cun to neighbour
                    shortest_distances[neighbour] = current_distance
                    # set neighbour's parent
                    predecessors[neighbour] = cun
                    # chance distance in priority queue
                    change_distance(calculated_distances, neighbour, current_distance)

        # also check if cun is 'G' and calculate shortest_path_any(cun, end_nodes, graph, True)
        if cun.value == 'G' and not teleports_activated:
            teleport_trace, _ = shortest_path_any(cun, end_nodes, graph, True)
            teleport_trace = gpt(predecessors, cun)[:-1] + teleport_trace

    # determine which Node from end_nodes set has lowest distance from start
    closest_end_node = list(end_nodes)
    gtd = get_trace_distance    # just alias
    reduce(lambda l, r: l if gtd(graph, gpt(predecessors, l)) < gtd(graph, gpt(predecessors, r)) else r,
           closest_end_node)
    closest_end_node = list(end_nodes)[0]

    foot_trace = gpt(predecessors, closest_end_node)

    return (foot_trace, teleports_activated) if not teleport_trace or gtd(graph, foot_trace) < gtd(graph, teleport_trace) \
        else (teleport_trace, True)


def shortest_path_all(source, end_nodes, graph, teleports_status=False):
    """
    Calculates shortest paths for all specified end_nodes
    :param source: source node, starting node
    :param end_nodes: set of destinations
    :param graph: graph with specified distances
    :param teleports_status: true if teleports are already activated, false otherwise
    :return: dictionary of {key: value}, exactly:
        {destination: (array_of_nodes, distance, teleport_activated)}
        - array_of_nodes: array of Nodes on shortest path
        - distance: sum of distances in array_of_nodes
        - teleport_activated: true if Node.value == 'G' is in array_of_nodes, (teleports are activated now on)
    """
    # todo: make this for all end_nodes
    # todo: use dynamic programming, look aside dict: {NodeA: {NodeB: 5}}, distance from A to B is 5
    # todo: | do not allow all 'caching', with 1000x1000 map = 1M nodes this yields to 1T integers
    def change_distance(q, u, d):
        """
        :param q: priority queue
        :param u: vertex
        :param d: new distance
        """
        for i, node in enumerate(q):
            if node[1] == u:
                q[i] = (d, node[1])
                break
        heapq.heapify(q)

    teleport_trace = None

    gpt = get_predecesors_trace     # just alias for that long function name

    # {Node(...): x, ...}       where x is distance from start node to Node
    shortest_distances = {node: sys.maxsize for node in graph.nodes.values()}
    shortest_distances[source] = 0       # where we start, its distance 0
    predecessors = {}       # {Node1(...): Node2(...), ...}         where Node1 is child of Node2

    # priority queue
    pq = [(0, node) if node == source else (sys.maxsize, node) for node in graph.nodes.values()]
    heapq.heapify(pq)

    done = set()       # nodes which already have shortest path calculated

    while pq:
        distance, cun = heapq.heappop(pq)        # cun = closest unprocessed node
        done.add(cun)
        neighbours = graph.get_neighbours(cun, teleports_status)
        for neighbour in neighbours:
            if neighbour not in done:
                current_distance = shortest_distances.get(cun) + graph.get_distance_to_neighbour(cun, neighbour)
                if current_distance < shortest_distances.get(neighbour):
                    # chance distance of neighbour to distance of cun + distance from cun to neighbour
                    shortest_distances[neighbour] = current_distance
                    # set neighbour's parent
                    predecessors[neighbour] = cun
                    # chance distance in priority queue
                    change_distance(pq, neighbour, current_distance)

        # if teleports are not activated yet then:
        # check if cun is 'G' and calculate shortest_path_any(cun, end_nodes, graph, True)
        if not teleports_status and cun.value == 'G':
            teleport_trace, _ = shortest_path_any(cun, end_nodes, graph, True)
            teleport_trace = gpt(predecessors, cun)[:-1] + teleport_trace

    # todo: foot_trace = gpt(predecessors, end_node1), ...

    pass
    # return {endNode: ([source, node, node, node, endNode], 5, True)} for example


def get_predecesors_trace(dictonary, destination):
    """
    Returns list containing trace from start to node, inside dictionary of predecesors
    :param dictonary: in shape {Node1(...): Node2(...)}     meaning Node1's parent is Node2
    :param destination: destination node which to calculate path
    :return: array of nodes from source to destination
    """
    if destination not in dictonary.keys():
        return []

    trace = [destination]

    current = destination
    while dictonary.get(current):
        current = dictonary.get(current)
        trace.append(current)

    return trace[::-1]      # reverse list, because on trace[0] is start and trace[n] is end


def get_trace_distance(graph, trace):
    """
    Returns sum of distances on specified trace
    :param graph: graph which to get distances
    :param trace: array of nodes
    :return: sum of distances of nodes inside trace, [] returns sys.maxsize
    """
    if not trace:
        return sys.maxsize

    distance = 0
    for i in range(1, len(trace)):
        distance += graph.get_distance_to_neighbour(trace[i-1], trace[i])
    return distance


def print_path(path, style='default'):
    if style in {'default', 'verbose'}:
        for node in path:
            print(node)
    elif style == 'minimal':
        for node in path:
            print('({},{})'.format(node.x, node.y))


def load_map_from_file(file):
    terrain_map = []
    with open(file, 'r') as f:
        for line in f:
            terrain_map.append(line.strip())
    return terrain_map


def save_princess(terrain, max_turns, verbose=False):
    graph = TerrainGraph(terrain)

    if not graph.princesses:
        if verbose:
            print('No princess to save.')
        return []

    dragon_path, teleport_active = shortest_path_any(graph.nodes.get((0, 0)), {graph.dragon}, graph)
    if verbose:
        print('To dragon its', get_trace_distance(graph, dragon_path), 'turns', 'with' if teleport_active else 'without',
              'teleport.')
        print_path(dragon_path)

    if get_trace_distance(graph, dragon_path) >= max_turns:
        if verbose:
            print('There is no hope to kill dragon in ' + str(max_turns) + ' turns.')
        return []

    # dragon slayed, time to save princesses, YAY
    # we need to save all princesses in smallest amount of time, (Travelling salesman problem)
    # since we have only 3 princesses we can try all 3! possible cases
    permutations = list(itertools.permutations(graph.princesses, len(graph.princesses)))

    first_try = True
    princesses_path = []
    princesses_distance = 0

    # saves already calculated paths (dynamic programming)
    calculated_paths = {}       # {((Node1(...), Node2(...), teleport_active): [Node1(...), Node3(...), ...]}
    for permutation in permutations:
        previous_place = graph.dragon   # where to start when looking for princesses
        current_princesses_path = []    # currently calculated path
        tp_on_now = teleport_active     # determined whether teleport is active this permutation

        for i in range(len(permutation)):
            princess = permutation[i]
            if (previous_place, princess, teleport_active) in calculated_paths.keys():  # already have calculated this
                princess_path = calculated_paths.get((previous_place, princess, tp_on_now))
            else:
                princess_path, tp_on_now = shortest_path_any(previous_place, {princess}, graph, tp_on_now)
                # save path to calculated_paths
                key = (previous_place, princess, teleport_active)
                calculated_paths[key] = princess_path[:]
                if tp_on_now:     # and if teleports are active, we can asume walking takes least this long
                    calculated_paths[(previous_place, princess, False)] = calculated_paths.get(key)

            # concat paths, we need joining Node only once, hence [:-1]
            current_princesses_path = current_princesses_path[:-1] + princess_path
            previous_place = princess

        # compare distances, winner is with lower distance cost
        if first_try or get_trace_distance(graph, current_princesses_path) < princesses_distance:
            princesses_path = current_princesses_path
            princesses_distance = get_trace_distance(graph, current_princesses_path)
            first_try = False

    if verbose:
        print('To collect all {} princeses its'.format(len(graph.princesses)), princesses_distance, 'turns.')
        print_path(princesses_path)

    return dragon_path[:-1] + princesses_path


def main():
    terrain = load_map_from_file('generated/3py.txt')
    turns = 1000
    path = save_princess(terrain, turns, True)
    #print(path)
    #print_path(path, 'verbose')
    print_path(path, 'minimal')

if __name__ == '__main__':
    main()
