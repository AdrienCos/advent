from dataclasses import dataclass
from pathlib import Path
import sys


EXAMPLE_INPUT = """
RRRRIICCFF
RRRRIICCCF
VVRRRCCFFF
VVRCCCJFFF
VVVVCJJCFE
VVIVCCJJEE
VVIIICJJEE
MIIIIIJJEE
MIIISIJEEE
MMMISSJEEE
"""

TEST_INPUT_1 = """
OOOOO
OXOXO
OOOOO
OXOXO
OOOOO
"""

TEST_INPUT_2 = """
AAAA
BBCD
BBCC
EEEC
"""

TEST_INPUT_3 = """
EEEEE
EXXXX
EEEEE
EXXXX
EEEEE
"""

TEST_INPUT_4 = """
AAAAAA
AAABBA
AAABBA
ABBAAA
ABBAAA
AAAAAA
"""

type Coords = tuple[int, int]
type Map[T] = list[list[T]]

DIRECTIONS: tuple[Coords, ...] = ((0, 1), (0, -1), (1, 0), (-1, 0))


@dataclass
class Filter:
    identical_cells: list[Coords]
    different_cells: list[Coords]


CORNER_FILTERS: list[Filter] = [
    # Internal corners
    Filter(identical_cells=[(0, 1), (1, 0)], different_cells=[(1, 1)]),
    Filter(identical_cells=[(0, 1), (-1, 0)], different_cells=[(-1, 1)]),
    Filter(identical_cells=[(0, -1), (1, 0)], different_cells=[(1, -1)]),
    Filter(identical_cells=[(0, -1), (-1, 0)], different_cells=[(-1, -1)]),
    # External corners
    Filter(identical_cells=[], different_cells=[(0, 1), (1, 0)]),
    Filter(identical_cells=[], different_cells=[(0, -1), (1, 0)]),
    Filter(identical_cells=[], different_cells=[(0, 1), (-1, 0)]),
    Filter(identical_cells=[], different_cells=[(0, -1), (-1, 0)]),
]


def match_filter(
    map: Map[str], map_size: tuple[int, int], center_coods: Coords, filter: Filter
) -> bool:
    height, width = map_size

    center_val = map[center_coods[0]][center_coods[1]]
    for offset in filter.identical_cells:
        should_match_line = center_coods[0] + offset[0]
        should_match_column = center_coods[1] + offset[1]
        if (
            should_match_line < 0
            or should_match_line >= height
            or should_match_column < 0
            or should_match_column >= width
        ):
            should_match_val = "-"
        else:
            should_match_val = map[should_match_line][should_match_column]

        if should_match_val != center_val:
            return False
    for offset in filter.different_cells:
        should_not_match_line = center_coods[0] + offset[0]
        should_not_match_column = center_coods[1] + offset[1]
        if (
            should_not_match_line < 0
            or should_not_match_line >= height
            or should_not_match_column < 0
            or should_not_match_column >= width
        ):
            should_not_match_val = "-"
        else:
            should_not_match_val = map[should_not_match_line][should_not_match_column]
        if should_not_match_val == center_val:
            return False
    return True


def build_corner_map(map: Map[str]) -> Map[int]:
    height = len(map)
    width = len(map[0])
    corners_map: Map[int] = [[0 for _ in range(width)] for _ in range(height)]
    for i in range(height):
        for j in range(width):
            corners = 0
            for filter in CORNER_FILTERS:
                if match_filter(map, (height, width), (i, j), filter):
                    corners += 1
            corners_map[i][j] = corners
    return corners_map


def build_perimeter_map(map: Map[str]) -> Map[int]:
    height = len(map)
    width = len(map[0])
    # Map of how much each cell will contribute to the perimeter
    perimeter_map: Map[int] = [[0 for _ in range(width)] for _ in range(height)]
    for i in range(height):
        for j in range(width):
            frontiers_count = 0
            for direction in DIRECTIONS:
                adj_line = i + direction[0]
                adj_col = j + direction[1]
                if (
                    adj_col < 0
                    or adj_col >= width
                    or adj_line < 0
                    or adj_line >= height
                ):
                    frontiers_count += 1
                elif map[adj_line][adj_col] != map[i][j]:
                    frontiers_count += 1
            perimeter_map[i][j] = frontiers_count
    return perimeter_map


def compute_cost(map: Map[str], cost_map: Map[int]) -> int:
    total_price = 0
    height = len(map)
    width = len(map[0])
    # Flood fill to find each region
    visited_cells: set[Coords] = set()
    for i in range(height):
        for j in range(width):
            # Check if the cell has already been accounted for
            if (i, j) in visited_cells:
                continue

            # This is a new region, flood fill it
            region_letter = map[i][j]
            cells_to_visit: set[Coords] = {(i, j)}
            region: set[Coords] = set()
            while len(cells_to_visit) != 0:
                current_cell = cells_to_visit.pop()
                region.add(current_cell)
                for direction in DIRECTIONS:
                    try:
                        adj_line = current_cell[0] + direction[0]
                        adj_col = current_cell[1] + direction[1]
                        if (
                            adj_col < 0
                            or adj_col >= width
                            or adj_line < 0
                            or adj_line >= height
                        ):
                            continue
                        if map[adj_line][adj_col] == region_letter:
                            if ((adj_line, adj_col)) not in region:
                                cells_to_visit.add((adj_line, adj_col))
                    except IndexError:
                        continue
            region_area = len(region)
            region_perimeter = 0
            for cell in region:
                region_perimeter += cost_map[cell[0]][cell[1]]
            region_price = region_area * region_perimeter
            total_price += region_price
            visited_cells |= region
    return total_price


def parse_input(input: str) -> Map[str]:
    map: Map[str] = []
    lines = input.strip().split("\n")
    for line in lines:
        row = [e for e in line]
        map.append(row)
    return map


def part1(input: str) -> int:
    map = parse_input(input)
    # Map of how much each cell will contribute to the perimeter
    perimeter_map = build_perimeter_map(map)
    total_price = compute_cost(map, perimeter_map)
    return total_price


def part2(input: str) -> int:
    map = parse_input(input)
    corners_map = build_corner_map(map)
    total_price = compute_cost(map, corners_map)

    return total_price


"""
Benchmark 1 (38 runs): ./venv/bin/python src/day12.py /tmp/.sops2709419432/tmp-file2039887272
    measurement          mean ± σ            min … max           outliers
    wall_time           131ms ± 4.55ms     125ms …  146ms          2 ( 5%)
    peak_rss           17.0MB ±  116KB    16.8MB … 17.2MB          0 ( 0%)
    cpu_cycles          459M  ± 11.1M      438M  …  495M           2 ( 5%)
    instructions       1.47G  ± 16.2M     1.39G  … 1.48G           4 (11%)
    cache_references   2.11M  ±  140K     1.79M  … 2.45M           0 ( 0%)
    cache_misses        387K  ±  163K      127K  …  755K           0 ( 0%)
    branch_misses      1.95M  ± 54.3K     1.80M  … 2.01M           3 ( 8%)
"""
if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_text = Path(sys.argv[1]).read_text()
    else:
        input_text = (
            Path(__file__).parent.parent / "inputs" / "2024" / "day12.txt"
        ).read_text()

    assert part1(TEST_INPUT_1) == 772
    assert part1(TEST_INPUT_2) == 140
    assert part1(EXAMPLE_INPUT) == 1930
    result1 = part1(input_text)
    print(result1)

    assert part2(TEST_INPUT_2) == 80
    assert part2(TEST_INPUT_1) == 436
    assert part2(TEST_INPUT_3) == 236
    assert part2(TEST_INPUT_4) == 368
    assert part2(EXAMPLE_INPUT) == 1206
    result2 = part2(input_text)
    print(result2)
