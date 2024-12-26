from functools import cache
from pathlib import Path
import sys
from typing import Literal

EXAMPLE_INPUT = """
###############
#.......#....E#
#.#.###.#.###.#
#.....#.#...#.#
#.###.#####.#.#
#.#.#.......#.#
#.#.#####.###.#
#...........#.#
###.#.#####.#.#
#...#.....#.#.#
#.#.#.###.#.#.#
#.....#...#.#.#
#.###.#.#.#.#.#
#S..#.....#...#
###############
"""

TEST_INPUT_1 = """
#################
#...#...#...#..E#
#.#.#.#.#.#.#.#.#
#.#.#.#...#...#.#
#.#.#.#.###.#.#.#
#...#.#.#.....#.#
#.#.#.#.#.#####.#
#.#...#.#.#.....#
#.#.#####.#.###.#
#.#.#.......#...#
#.#.###.#####.###
#.#.#...#.....#.#
#.#.#.#####.###.#
#.#.#.........#.#
#.#.#.#########.#
#S#.............#
#################
"""

TEST_INPUT_2 = """
#####
#..E#
#...#
#S..#
#####
"""

TEST_INPUT_3 = """
#####
#S.E#
#####
"""


type Coords = tuple[int, int]
type Axis = Literal["v", "h"]
type CoordsAndAxis = tuple[Coords, Axis]
# String in the form "$xpos_$ypos_$axis"
type NodeId = str
type Cost = int
type HeuristicValue = int
type Graph = dict[NodeId, list[tuple[Cost, NodeId]]]

FLOOR = "."
WALL = "#"
START = "S"
END = "E"
UP = (-1, 0)
DOWN = (1, 0)
LEFT = (0, 1)
RIGHT = (0, -1)
DIRECTIONS = (UP, DOWN, LEFT, RIGHT)
UPDOWN = (UP, DOWN)
LEFTRIGHT = (LEFT, RIGHT)


class NoNextNodeFoundError(Exception):
    pass


class InvalidIdError(Exception):
    pass


def move(pos: Coords, direction: Coords) -> Coords:
    return (pos[0] + direction[0], pos[1] + direction[1])


class Map:
    _grid: list[list[str]]
    # How to interpret:
    # When entering cell N from axis X, lookup graph[(N,X)]
    # It provides a list of reachable cells, the axis used to travel to them, and the cost to reach them
    graph: Graph
    width: int
    height: int
    start: Coords
    end: Coords

    def __init__(self, grid: list[list[str]]) -> None:
        self.height = len(grid)
        self.width = len(grid[0])
        self.graph = {}
        self._grid = grid
        for i, line in enumerate(grid):
            if START in line:
                self.start = (i, line.index(START))
            if END in line:
                self.end = (i, line.index(END))

    def build_graph(self) -> None:
        for line_idx in range(self.height):
            for col_idx in range(self.width):
                if self.grid((line_idx, col_idx)) == WALL:
                    continue

                vert_edges: list[tuple[Cost, NodeId]] = []
                hor_edges: list[tuple[Cost, NodeId]] = []

                for direction in UPDOWN:
                    adj_coords = move((line_idx, col_idx), direction)
                    if self.is_oob(adj_coords):
                        continue
                    if self.grid(adj_coords) == WALL:
                        continue
                    # Add edge of weight 1 for movement in same direction
                    vert_edges.append(
                        (
                            1,
                            coords_and_axis_to_id(adj_coords, "v"),
                        )
                    )
                    # Add edge of weigth 1000 for movement in different direction
                    hor_edges.append(
                        (
                            1_001,
                            coords_and_axis_to_id(adj_coords, "v"),
                        )
                    )

                for direction in LEFTRIGHT:
                    adj_coords = move((line_idx, col_idx), direction)
                    if self.is_oob(adj_coords):
                        continue
                    if self.grid(adj_coords) == WALL:
                        continue
                    # Add edge of weigth 1000 for movement in different direction
                    vert_edges.append(
                        (
                            1_001,
                            coords_and_axis_to_id(adj_coords, "h"),
                        )
                    )
                    # Add edge of weight 1 for movement in same direction
                    hor_edges.append(
                        (
                            1,
                            coords_and_axis_to_id(adj_coords, "h"),
                        )
                    )
                self.graph[coords_and_axis_to_id((line_idx, col_idx), "v")] = vert_edges
                self.graph[coords_and_axis_to_id((line_idx, col_idx), "h")] = hor_edges

        # Link the end cells together for free
        self.graph[coords_and_axis_to_id(self.end, "v")].append(
            ((0, coords_and_axis_to_id(self.end, "h")))
        )
        self.graph[coords_and_axis_to_id(self.end, "h")].append(
            (0, coords_and_axis_to_id(self.end, "v"))
        )

    def grid(self, pos: Coords) -> str:
        return self._grid[pos[0]][pos[1]]

    def is_oob(self, cell: Coords) -> bool:
        if (
            cell[0] < 0
            or cell[0] >= self.height
            or cell[1] < 0
            or cell[1] >= self.width
        ):
            return True
        return False

    def find_cheapest_path(self) -> int:
        # Do a dijkstra without a priority queue
        dist: dict[NodeId, int] = {}
        prev: dict[NodeId, NodeId | None] = {}
        # Let's just pretend this is a priority queue
        # Actually, we bin nodes in lists based on their currently estimated cost
        queue: dict[Cost, list[NodeId]] = {0: [], sys.maxsize: []}

        # Initialize the data structures
        for vertex in self.graph.keys():
            dist[vertex] = sys.maxsize
            prev[vertex] = None
            if vertex != coords_and_axis_to_id(self.start, "h"):
                queue[sys.maxsize].append(vertex)
            else:
                queue[0].append(vertex)
        dist[coords_and_axis_to_id(self.start, "h")] = 0

        # Run the search
        end_vert_node = coords_and_axis_to_id(self.end, "v")
        end_hor_node = coords_and_axis_to_id(self.end, "h")
        next_node = None
        while len(queue) > 0:
            # Get the entry with the lower value
            next_dist = min(queue.keys())
            next_node = queue[next_dist].pop()
            if queue[next_dist] == []:
                del queue[next_dist]
            if next_node == end_hor_node or next_node == end_vert_node:
                break

            for neighbor in self.graph[next_node]:
                alt = next_dist + neighbor[0]
                if alt < dist[neighbor[1]]:
                    queue[dist[neighbor[1]]].remove(neighbor[1])
                    if queue[dist[neighbor[1]]] == []:
                        del queue[dist[neighbor[1]]]
                    if alt not in queue:
                        queue[alt] = []
                    queue[alt].append(neighbor[1])
                    dist[neighbor[1]] = alt
                    prev[neighbor[1]] = next_node

        # Traceback through the prev dict to find the path
        # next_node contains the actual node of the end
        if next_node is None:
            raise NoNextNodeFoundError
        cost = dist[next_node]

        return cost


@cache
def coords_and_axis_to_id(pos: Coords, axis: Axis) -> NodeId:
    id = f"{pos[0]}_{pos[1]}_{axis}"
    return id


@cache
def id_to_coords_and_axis(id: NodeId) -> CoordsAndAxis:
    x_str, y_str, axis = id.split("_")
    pos = (int(x_str), int(y_str))
    if axis == "v":
        return (pos, "v")
    elif axis == "h":
        return (pos, "h")
    raise InvalidIdError(id)


def parse_input(input: str) -> Map:
    lines = input.strip().split("\n")
    grid: list[list[str]] = []
    for line in lines:
        grid.append([e for e in line])
    return Map(grid)


def part1(input: str) -> int:
    map = parse_input(input)
    map.build_graph()
    cost = map.find_cheapest_path()
    return cost


def part2(input: str) -> int:
    count = 0
    return count


"""
"""
if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_text = Path(sys.argv[1]).read_text()
    else:
        input_text = (
            Path(__file__).parent.parent / "inputs" / "2024" / "day16.txt"
        ).read_text()

    assert part1(TEST_INPUT_3) == 2
    assert part1(TEST_INPUT_2) == 1004
    assert part1(EXAMPLE_INPUT) == 7036
    assert part1(TEST_INPUT_1) == 11048
    result1 = part1(input_text)
    print(result1)

    assert part2(EXAMPLE_INPUT) == -1
    result2 = part2(input_text)
    print(result2)
