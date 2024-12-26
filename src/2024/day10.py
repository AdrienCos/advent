from pathlib import Path
import sys


EXAMPLE_INPUT = """
89010123
78121874
87430965
96549874
45678903
32019012
01329801
10456732
"""

# One trail
TEST_INPUT_1 = """
01234
98765
"""
# One trail
TEST_INPUT_2 = """
012
543
678
009
"""
# Two trails with different starts and same end
TEST_INPUT_3 = """
01234
98765
01234
"""
# Two trails with different starts and same end
TEST_INPUT_4 = """
090
181
272
363
454
"""
# Two trails with the same start and end
TEST_INPUT_5 = """
505
515
525
434
505
606
787
090
"""
# Two trails with the same start and different ends
TEST_INPUT_6 = """
98765
01234
98765
"""

type Map = list[list[int]]
type Coords = tuple[int, int]

DIRECTIONS: list[Coords] = [(0, 1), (0, -1), (1, 0), (-1, 0)]


def parse_input(input: str) -> Map:
    lines = input.strip().split("\n")
    map: Map = []
    for line in lines:
        map.append([int(e) for e in line])
    return map


def part1(input: str) -> int:
    map = parse_input(input)
    height = len(map)
    width = len(map[0])
    trailheads = [(i, j) for i in range(height) for j in range(width) if map[i][j] == 0]
    count = 0
    for trailhead in trailheads:
        heads = [(trailhead, map[trailhead[0]][trailhead[1]])]
        ends: list[Coords] = []
        while len(heads) > 0:
            head_pos, head_val = heads.pop()
            # Look around the adjacent cells
            for dir in DIRECTIONS:
                adj_line = head_pos[0] + dir[0]
                adj_col = head_pos[1] + dir[1]
                # Ignore OOB
                if (
                    adj_line < 0
                    or adj_line >= height
                    or adj_col < 0
                    or adj_col >= width
                ):
                    continue
                adj_val = map[adj_line][adj_col]
                if adj_val == head_val + 1:
                    new_potential_head = ((adj_line, adj_col), head_val + 1)
                    if adj_val == 9 and (adj_line, adj_col) not in ends:
                        count += 1
                        ends.append((adj_line, adj_col))
                    elif new_potential_head not in heads:
                        heads.append(new_potential_head)

    return count


def part2(input: str) -> int:
    map = parse_input(input)
    height = len(map)
    width = len(map[0])
    # Build a map of how many times each location was traversed
    shadow_map = [[0 for _ in range(width)] for _ in range(height)]
    # Set all the tiles at height 0 to a traversal count of 1
    for i in range(height):
        for j in range(width):
            if map[i][j] == 0:
                shadow_map[i][j] = 1

    trail_heads: set[Coords] = set(
        [(i, j) for i in range(height) for j in range(width) if map[i][j] == 0]
    )
    # Iterate over each height level (except 9)
    for i in range(9):
        next_trail_heads: set[Coords] = set()
        for head in trail_heads:
            # Check each adjacent cell
            for direction in DIRECTIONS:
                adj_line = head[0] + direction[0]
                adj_col = head[1] + direction[1]
                if (
                    adj_line < 0
                    or adj_line >= height
                    or adj_col < 0
                    or adj_col >= width
                ):
                    continue

                neighbour = map[adj_line][adj_col]
                if neighbour == i + 1:
                    # This cell is a continuation of the trail
                    shadow_map[adj_line][adj_col] += shadow_map[head[0]][head[1]]
                    next_trail_heads.add((adj_line, adj_col))
        trail_heads = next_trail_heads

    # Count the number of trails leading to each cell of value '9'
    count = 0
    for i in range(height):
        for j in range(width):
            if map[i][j] == 9:
                count += shadow_map[i][j]
    return count


"""
Benchmark 1 (157 runs): ./venv/bin/python src/day10.py /tmp/.sops1870891364/tmp-file3033514338
    measurement          mean ± σ            min … max           outliers
    wall_time          31.8ms ± 4.47ms    27.2ms … 48.3ms          8 ( 5%)
    peak_rss           12.7MB ± 86.0KB    12.4MB … 12.8MB          0 ( 0%)
    cpu_cycles         88.3M  ± 9.58M     46.0M  …  105M          19 (12%)
    instructions        197M  ± 14.8M      130M  …  207M          11 ( 7%)
    cache_references   1.04M  ±  106K      592K  … 1.25M           7 ( 4%)
    cache_misses        127K  ± 73.5K     29.4K  …  310K           0 ( 0%)
    branch_misses       738K  ± 99.0K      268K  …  818K          15 (10%)
"""
if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_text = Path(sys.argv[1]).read_text()
    else:
        input_text = (
            Path(__file__).parent.parent / "inputs" / "2024" / "day10.txt"
        ).read_text()

    assert part1(TEST_INPUT_1) == 1
    assert part1(TEST_INPUT_2) == 1
    assert part1(TEST_INPUT_3) == 2
    assert part1(TEST_INPUT_4) == 2
    assert part1(TEST_INPUT_5) == 1
    assert part1(TEST_INPUT_6) == 2
    assert part1(EXAMPLE_INPUT) == 36
    result1 = part1(input_text)
    print(result1)

    assert part2(EXAMPLE_INPUT) == 81
    result2 = part2(input_text)
    print(result2)
