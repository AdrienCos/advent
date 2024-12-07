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

# True means obstructed, False means open
type Map = list[list[bool]]
# Order is line, column
type Coordinates = tuple[int, int]


class Direction(enum.Enum):
    UP = (-1, 0)
    RIGHT = (0, 1)
    DOWN = (1, 0)
    LEFT = (0, -1)


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


def project_ray(map: Map, pos: Coordinates, direction: Direction) -> set[Coordinates]:
    ray: set[Coordinates] = {pos}
    while True:
        pos = move(pos, direction)
        if (
            pos[0] < 0
            or pos[0] >= len(map)
            or pos[1] < 0
            or pos[1] >= len(map[0])
            or map[pos[0]][pos[1]]
        ):
            return ray
        ray.add(pos)


def part1(input: str) -> int:
    map, guard_pos, guard_dir = parse_input(input)
    # Guard's starting postion is always visited
    visited: set[Coordinates] = {guard_pos}
    guard_has_left = False
    while not guard_has_left:
        new_pos = move(guard_pos, guard_dir)
        # Is the new position out of bounds ?
        if (
            new_pos[0] < 0
            or new_pos[0] >= len(map)
            or new_pos[1] < 0
            or new_pos[1] >= len(map[0])
        ):
            # The guard has left the map
            guard_has_left = True
        elif not map[new_pos[0]][new_pos[1]]:
            # The cell is free, the guard moves there
            visited.add(new_pos)
            guard_pos = new_pos
        else:
            # The cell is obstructed, the guard turns right
            guard_dir = turn_right(guard_dir)
    return len(visited)


def part2(input: str) -> int:
    map, guard_pos, guard_dir = parse_input(input)
    # Cells visited by direction
    visited: dict[Direction, set[Coordinates]] = {
        Direction.UP: {guard_pos},
        Direction.DOWN: set(),
        Direction.LEFT: set(),
        Direction.RIGHT: set(),
    }
    # Cast a ray towards the back of the guard's starting position
    virtually_visited = project_ray(map, guard_pos, turn_back(guard_dir))
    visited[guard_dir] |= virtually_visited

    obstacles: set[Coordinates] = set()
    guard_has_left = False
    count = 0
    while not guard_has_left:
        new_pos = move(guard_pos, guard_dir)
        # Obstacle case #1: Have we already visited this cell while going in the
        # next direction before?
        if guard_pos in visited[turn_right(guard_dir)]:
            obstacles.add(new_pos)
            count += 1
        # Is the new position out of bounds ?
        if (
            new_pos[0] < 0
            or new_pos[0] >= len(map)
            or new_pos[1] < 0
            or new_pos[1] >= len(map[0])
        ):
            # The guard has left the map
            guard_has_left = True
        elif not map[new_pos[0]][new_pos[1]]:
            # The cell is free, the guard moves there
            visited[guard_dir].add(new_pos)
            guard_pos = new_pos
        else:
            # The cell is obstructed, the guard turns right
            guard_dir = turn_right(guard_dir)
            visited[guard_dir].add(guard_pos)
            # Cast a ray behind the guard, flag all the cells as "visited"
            # This will be used by the obstacle case #1
            virtually_visited = project_ray(map, guard_pos, turn_back(guard_dir))
            visited[guard_dir] |= virtually_visited
    return count


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

    result = part2(
        """
....#.......
...........#
....^.......
...#........
............
..........#.
    """
    )
    print(result)

    assert part2(EXAMPLE_INPUT) == 6
    result2 = part2(INPUT_TEXT)
    print(result2)
