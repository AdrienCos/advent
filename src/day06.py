from copy import deepcopy
import enum
from pathlib import Path
import sys

EXAMPLE_INPUT = """
....#.....
.........#
..........
..#.......
.......#..
..........
.#..^.....
........#.
#.........
......#...
"""

TEST_INPUT_1 = """
....#.......
...........#
....^.......
...#........
............
..........#.
"""

TEST_INPUT_2 = """
....#.......
...........#
....^.......
............
..........#.
"""

TEST_INPUT_3 = """
########
#......#
...^...#
########
"""

TEST_INPUT_4 = """
....
#..#
.^#.
"""

TEST_INPUT_5 = """
###
..#
^##
"""

TEST_INPUT_6 = """
##..
...#
....
^.#.
"""

# True means obstructed, False means open
type Map = list[list[bool]]
# Order is line, column
type Coordinates = tuple[int, int]


class Direction(enum.Enum):
    UP = (-1, 0)
    RIGHT = (0, 1)
    DOWN = (1, 0)
    LEFT = (0, -1)


type Step = tuple[Coordinates, Direction]


def turn_right(direction: Direction) -> Direction:
    return Direction((direction.value[1], -direction.value[0]))


def turn_back(direction: Direction) -> Direction:
    return Direction((-direction.value[0], -direction.value[1]))


def move(pos: Coordinates, direction: Direction) -> Coordinates:
    return (pos[0] + direction.value[0], pos[1] + direction.value[1])


def parse_input(input: str) -> tuple[Map, Coordinates, Direction]:
    lines = input.strip().split("\n")
    map: Map = []
    guard_location = (-1, -1)
    for i, line in enumerate(lines):
        map.append([char == "#" for char in line])
        guard_column = line.find("^")
        if guard_column != -1:
            guard_location = (i, guard_column)
    return (map, guard_location, Direction.UP)


def compute_path(
    map: Map,
    guard_pos: Coordinates,
    guard_dir: Direction,
    already_visited: set[Step] | None = None,
) -> list[Step] | None:
    # Guard's starting postion is always visited
    visited: set[Step] = (
        {(guard_pos, guard_dir)} if already_visited is None else already_visited.copy()
    )
    path: list[Step] = [(guard_pos, guard_dir)]
    guard_has_left = False
    while not guard_has_left:
        new_pos = move(guard_pos, guard_dir)
        # Is the new position out of bounds ?
        if ((new_pos, guard_dir)) in visited:
            # The guard has entered a loop, stop here
            return None
        if (
            new_pos[0] < 0
            or new_pos[0] >= len(map)
            or new_pos[1] < 0
            or new_pos[1] >= len(map[0])
        ):
            # The guard has left the map
            guard_has_left = True
            break
        elif not map[new_pos[0]][new_pos[1]]:
            # The cell is free, the guard moves there
            visited.add((new_pos, guard_dir))
            path.append((new_pos, guard_dir))
            guard_pos = new_pos
        else:
            # The cell is obstructed, the guard turns right
            guard_dir = turn_right(guard_dir)
            visited.add((guard_pos, guard_dir))
            # path.append((new_pos, guard_dir))
    return path


def part1(input: str) -> int:
    map, guard_pos, guard_dir = parse_input(input)
    # Guard's starting postion is always visited
    path = compute_path(map, guard_pos, guard_dir)
    assert isinstance(path, list)
    return len(set([step[0] for step in path]))


def part2_fixed(input: str) -> int:
    map, guard_pos, guard_dir = parse_input(input)
    # Compute the path (pos+dir) once
    clear_path = compute_path(map, guard_pos, guard_dir)
    # Assert to make type checker happy
    assert isinstance(clear_path, list)

    obstacles: set[Coordinates] = set()
    # For each step of the path:
    for i, step in enumerate(clear_path[:-1]):
        # Place an obstacle on the next step
        obstacle_coords = clear_path[i + 1]
        if obstacle_coords[0] == guard_pos:
            # We cannot place an obstacle on the guard's initial spot
            continue
        if obstacle_coords[0] in [step[0] for step in clear_path[:i]]:
            # We cannot place an obstacle on a cell already traversed by the guard
            continue
        # FIXME: optimize this by not copying the map by applying a mask on it
        map_with_obstacles = deepcopy(map)
        map_with_obstacles[obstacle_coords[0][0]][obstacle_coords[0][1]] = True
        # Try to solve the rest of the path, using the path so far
        path_or_fail = compute_path(
            map_with_obstacles, step[0], step[1], set(clear_path[:i])
        )
        # If the solve fails, we entered a loop, so the obstacle is useful
        if path_or_fail is None:
            obstacles.add(obstacle_coords[0])
    return len(obstacles)


"""
Benchmark 1 (79 runs): python src/day05.py
    measurement          mean ± σ            min … max           outliers
    wall_time          63.6ms ± 4.56ms    59.1ms … 80.5ms          4 ( 5%)
    peak_rss           13.0MB ±  120KB    12.7MB … 13.2MB          1 ( 1%)
    cpu_cycles          208M  ± 8.44M      173M  …  227M           6 ( 8%)
    instructions        620M  ± 12.2M      561M  …  627M           6 ( 8%)
    cache_references   1.10M  ± 93.3K      709K  … 1.27M           1 ( 1%)
    cache_misses        253K  ± 50.3K      148K  …  396K           0 ( 0%)
    branch_misses       901K  ± 80.0K      491K  …  960K           9 (11%)
"""
if __name__ == "__main__":
    if len(sys.argv) > 1:
        INPUT_TEXT = Path(sys.argv[1]).read_text()
    else:
        INPUT_TEXT = (Path(__file__).parent.parent / "inputs" / "day06.txt").read_text()

    assert part1(EXAMPLE_INPUT) == 41
    result1 = part1(INPUT_TEXT)
    print(result1)

    assert part2_fixed(EXAMPLE_INPUT) == 6
    assert part2_fixed(TEST_INPUT_1) == 2
    assert part2_fixed(TEST_INPUT_2) == 1
    assert part2_fixed(TEST_INPUT_3) == 6
    assert part2_fixed(TEST_INPUT_4) == 1
    assert part2_fixed(TEST_INPUT_5) == 0
    assert part2_fixed(TEST_INPUT_6) == 0
    result2 = part2_fixed(INPUT_TEXT)
    print(result2)
