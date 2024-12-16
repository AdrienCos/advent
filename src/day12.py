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


def parse_input(input: str) -> Map[str]:
    map: Map[str] = []
    lines = input.strip().split("\n")
    for line in lines:
        row = [e for e in line]
        map.append(row)
    return map


def part1(input: str) -> int:
    map = parse_input(input)
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

    total_price = 0
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
                region_perimeter += perimeter_map[cell[0]][cell[1]]
            region_price = region_area * region_perimeter
            total_price += region_price
            visited_cells |= region
    return total_price


def part2(input: str) -> int:
    _ = parse_input(input)
    return 0


"""
"""
if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_text = Path(sys.argv[1]).read_text()
    else:
        input_text = (Path(__file__).parent.parent / "inputs" / "day12.txt").read_text()

    assert part1(TEST_INPUT_1) == 772
    assert part1(TEST_INPUT_2) == 140
    assert part1(EXAMPLE_INPUT) == 1930
    result1 = part1(input_text)
    print(result1)

    assert part1(TEST_INPUT_2) == 80
    assert part1(TEST_INPUT_1) == 436
    assert part1(TEST_INPUT_3) == 236
    assert part1(TEST_INPUT_4) == 368
    assert part2(EXAMPLE_INPUT) == 1206
    result2 = part2(input_text)
    print(result2)
