from pathlib import Path
import sys

EXAMPLE_INPUT = """
###############
#...#...#.....#
#.#.#.#.#.###.#
#S#...#.#.#...#
#######.#.#.###
#######.#.#...#
#######.#.###.#
###..E#...#...#
###.#######.###
#...###...#...#
#.#####.#.###.#
#.#...#.#.#...#
#.#.#.#.#.#.###
#...#...#...###
###############
"""

type Coords = tuple[int, int]
# True is free path, False is wall
type Cell = bool
type Track = dict[Coords, int]

DIRECTIONS: list[Coords] = [
    (0, 1),
    (0, -1),
    (1, 0),
    (-1, 0),
]


class Map:
    _grid: list[list[Cell]]
    start: Coords
    end: Coords
    height: int
    width: int

    def __init__(self, grid: list[list[Cell]], start: Coords, end: Coords) -> None:
        self._grid = grid
        self.start = start
        self.end = end
        self.height = len(grid)
        self.width = len(grid[0])

    def is_oob(self, cell: Coords) -> bool:
        if (
            cell[0] < 0
            or cell[0] >= self.height
            or cell[1] < 0
            or cell[1] >= self.width
        ):
            return True
        return False

    def grid(self, line_idx: int, col_idx: int) -> bool:
        return self._grid[line_idx][col_idx]

    @property
    def track(self) -> Track:
        """Compute and return the path between self.start and self.end

        We assume that there are no forks in the path, that the starting cell has
        a single path accessible from it.

        Returns:
            list[Coords]: Path between start and end
        """
        track: Track = {self.start: 0}
        step_nb = 1
        current_cell = self.start
        while current_cell != self.end:
            for direction in DIRECTIONS:
                adj_line = current_cell[0] + direction[0]
                adj_col = current_cell[1] + direction[1]
                if self.is_oob((adj_line, adj_col)):
                    continue
                if not self.grid(adj_line, adj_col):
                    continue
                if (adj_line, adj_col) in track:
                    continue
                current_cell = (adj_line, adj_col)
                track[current_cell] = step_nb
                step_nb += 1
                break
        return track

    def neiboring_cells(self, center: Coords, max_dist: int) -> list[Coords]:
        """Returns a list of cells within an L1 distance of `max_dist` of
        `center`.
        """
        neighbors: list[Coords] = []
        for line_offset in range(-max_dist, max_dist + 1):
            for col_offset in range(
                -(max_dist - abs(line_offset)), (max_dist - abs(line_offset)) + 1
            ):
                adj_line = center[0] + line_offset
                adj_col = center[1] + col_offset
                if self.is_oob((adj_line, adj_col)):
                    continue
                potential_neighbor = (adj_line, adj_col)
                neighbors.append(potential_neighbor)

        return neighbors


def l1_distance(a: Coords, b: Coords) -> int:
    delta_x = a[0] - b[0]
    delta_y = a[1] - b[1]
    dist = abs(delta_x) + abs(delta_y)
    return dist


def evaluate_cheat(
    track: Track,
    cheat_start: Coords,
    cheat_end: Coords,
    max_cheat_duration: int,
) -> int:
    """Computes the time saved by a cheat, defined by its start and end positions.

    If the cheat start or end are not on the path, -1 is returned.
    If the cheat is not allowed, -1 is returned.
    If the cheat is allowed but does not save time, 0 is returned.
    Else, the number of steps of `path` skipped minus the length of the cheat is returned.
    """
    if cheat_start not in track:
        return -1
    if cheat_end not in track:
        return -1
    cheat_duration = l1_distance(cheat_start, cheat_end)
    if cheat_duration > max_cheat_duration:
        return -1
    cheat_start_index = track[cheat_start]
    cheat_end_index = track[cheat_end]
    nb_steps_skipped = cheat_end_index - cheat_start_index
    actual_time_saved = nb_steps_skipped - cheat_duration
    return max(actual_time_saved, 0)


def parse_input(input: str) -> Map:
    lines = input.strip().split("\n")
    base_grid = [[False if e == "#" else True for e in line] for line in lines]
    start_coords = (-1, -1)
    end_coords = (-1, -1)
    for line_idx, line in enumerate(lines):
        for col_idx, cell in enumerate(line):
            if cell == "S":
                start_coords = (line_idx, col_idx)
            elif cell == "E":
                end_coords = (line_idx, col_idx)
    return Map(grid=base_grid, start=start_coords, end=end_coords)


def part1(input: str, min_time_save: int) -> int:
    map = parse_input(input)
    track = map.track

    nb_useful_cheats = 0
    for cheat_start in track.keys():
        # Look at all the cells in a 2-step radius around this cell
        cheat_ends = map.neiboring_cells(cheat_start, 2)
        for cheat_end in cheat_ends:
            if evaluate_cheat(track, cheat_start, cheat_end, 2) < min_time_save:
                continue
            nb_useful_cheats += 1

    return nb_useful_cheats


def part2(input: str, min_time_save: int) -> int:
    map = parse_input(input)
    track = map.track

    nb_useful_cheats = 0
    for cheat_start in track.keys():
        # Look at all the cells in a 20-step radius around this cell
        cheat_ends = map.neiboring_cells(cheat_start, 20)
        for cheat_end in cheat_ends:
            if evaluate_cheat(track, cheat_start, cheat_end, 20) < min_time_save:
                continue
            nb_useful_cheats += 1

    return nb_useful_cheats


"""
Benchmark 1: ./venv/bin/python src/day20.py /var/folders/fm/891_8yt158b05hy09ypkjyt40000gn/T/.sops2828868702/tmp-file4111857357
    Time (mean ± σ):      5.015 s ±  0.206 s    [User: 4.901 s, System: 0.033 s]
    Range (min … max):    4.845 s …  5.469 s    10 runs
"""
if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_text = Path(sys.argv[1]).read_text()
    else:
        input_text = (Path(__file__).parent.parent / "inputs" / "day20.txt").read_text()

    assert part1(EXAMPLE_INPUT, 1) == 44
    result1 = part1(input_text, 100)
    print(result1)

    assert part2(EXAMPLE_INPUT, 50) == 285
    result2 = part2(input_text, 100)
    print(result2)
