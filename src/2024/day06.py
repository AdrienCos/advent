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

# Order is line, column
type Coordinates = tuple[int, int]
type Direction = tuple[int, int]
type Step = tuple[Coordinates, Direction]


# True means obstructed, False means open
class Map:
    _map: list[list[bool]]
    _patch: Coordinates | None
    lines: int
    columns: int

    def patch(self, coords: Coordinates) -> None:
        self._patch = coords

    def unpatch(self) -> None:
        self._patch = None

    def __init__(self, map: list[list[bool]]) -> None:
        self._map = map
        self._patch = None
        self.lines = len(map)
        self.columns = len(map[0])

    def __call__(self, coords: Coordinates) -> bool | None:
        if coords == self._patch:
            return True
        if (
            coords[0] < 0
            or coords[0] >= self.lines
            or coords[1] < 0
            or coords[1] >= self.columns
        ):
            return None
        return self._map[coords[0]][coords[1]]

    def walk(
        self, start: Coordinates, direction: Direction
    ) -> tuple[bool, Coordinates, list[Step]]:
        # Return True if we left the map
        pos = start
        walk_steps: list[Step] = []
        while True:
            new_pos = move(pos, direction)
            new_cell = self(new_pos)
            if new_cell is None:
                # Out of the map
                return (True, pos, walk_steps)
            elif new_cell:
                # We are against an obstacle, stop there
                return (False, pos, walk_steps)
            else:
                # We take another step
                pos = new_pos
                walk_steps.append((pos, direction))


def turn_right(direction: Direction) -> Direction:
    return (direction[1], -direction[0])


def move(pos: Coordinates, direction: Direction) -> Coordinates:
    return (pos[0] + direction[0], pos[1] + direction[1])


def parse_input(input: str) -> tuple[Map, Coordinates, Direction]:
    lines = input.strip().split("\n")
    raw_map: list[list[bool]] = []
    guard_location = (-1, -1)
    for i, line in enumerate(lines):
        raw_map.append([char == "#" for char in line])
        guard_column = line.find("^")
        if guard_column != -1:
            guard_location = (i, guard_column)
    return (Map(raw_map), guard_location, (-1, 0))


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
        has_left, final_pos, walk_steps = map.walk(guard_pos, guard_dir)
        if set(walk_steps).intersection(visited):
            # The guard has entered a loop, stop here
            return None
        if has_left:
            # The guard has left the map, records the last steps and leave
            visited |= set(walk_steps)
            path += list(walk_steps)
            guard_has_left = True
            break
        else:
            # The guard has not left yet, and is facing an obstacle
            visited |= set(walk_steps)
            path += list(walk_steps)
            guard_dir = turn_right(guard_dir)
            guard_pos = final_pos
    return path


def part1(input: str) -> int:
    map, guard_pos, guard_dir = parse_input(input)
    # Guard's starting postion is always visited
    path = compute_path(map, guard_pos, guard_dir)
    assert isinstance(path, list)
    return len(set([step[0] for step in path]))


def part2(input: str) -> int:
    map, guard_pos, guard_dir = parse_input(input)
    # Compute the path (pos+dir) once
    clear_path = compute_path(map, guard_pos, guard_dir)
    # Assert to make type checker happy
    assert isinstance(clear_path, list)

    obstacles: set[Coordinates] = set()
    # For each step of the path:
    for i, step in enumerate(clear_path[:-1]):
        # Place an obstacle on the next step
        obstacle_coords = clear_path[i + 1][0]
        if obstacle_coords == guard_pos:
            # We cannot place an obstacle on the guard's initial spot
            continue
        if obstacle_coords in [step[0] for step in clear_path[:i]]:
            # We cannot place an obstacle on a cell already traversed by the guard
            continue
        map.patch(obstacle_coords)
        # Try to solve the rest of the path, using the path so far
        path_or_fail = compute_path(
            map,
            step[0],
            step[1],
            set(clear_path[:i]),
        )
        # Remove the patch
        map.unpatch()
        # If the solve fails, we entered a loop, so the obstacle is useful
        if path_or_fail is None:
            obstacles.add(obstacle_coords)
    return len(obstacles)


"""
Benchmark 1 (3 runs): ./venv/bin/python src/day06.py /tmp/.sops3742241049/tmp-file1905588157
    measurement          mean ± σ            min … max           outliers
    wall_time          3.73s  ± 38.3ms    3.71s  … 3.78s           0 ( 0%)
    peak_rss           17.1MB ± 34.4KB    17.0MB … 17.1MB          0 ( 0%)
    cpu_cycles         17.4G  ±  197M     17.2G  … 17.6G           0 ( 0%)
    instructions       38.0G  ± 5.76M     37.9G  … 38.0G           0 ( 0%)
    cache_references    772M  ± 3.61M      768M  …  775M           0 ( 0%)
    cache_misses       14.4M  ± 2.77M     12.1M  … 17.5M           0 ( 0%)
    branch_misses       116M  ± 4.91M      113M  …  122M           0 ( 0%)
"""
if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_text = Path(sys.argv[1]).read_text()
    else:
        input_text = (
            Path(__file__).parent.parent / "inputs" / "2024" / "day06.txt"
        ).read_text()

    assert part1(EXAMPLE_INPUT) == 41
    result1 = part1(input_text)
    print(result1)

    assert part2(EXAMPLE_INPUT) == 6
    assert part2(TEST_INPUT_1) == 2
    assert part2(TEST_INPUT_2) == 1
    assert part2(TEST_INPUT_3) == 6
    assert part2(TEST_INPUT_4) == 1
    assert part2(TEST_INPUT_5) == 0
    assert part2(TEST_INPUT_6) == 0
    result2 = part2(input_text)
    print(result2)
