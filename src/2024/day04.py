from pathlib import Path
import sys
import numpy as np

EXAMPLE_INPUT = """
MMMSXXMASM
MSAMXMSMSA
AMXSXMAAMM
MSAMASMSMX
XMASAMXAMM
XXAMMXXAMA
SMSMSASXSS
SAXAMASAAA
MAMMMXMMMM
MXMXAXMASX
"""


def parse_input(input: str):
    # Parse a string into a 2d numpy matrix
    return np.array([list(line) for line in input.strip().split("\n")])


def part1(input: str) -> int:
    grid = parse_input(input)
    count = 0
    # Horizonal
    for line in grid:
        line_str = "".join(line)
        count += (line_str).count("XMAS")
        count += (line_str).count("SAMX")
    # Vertical
    for column in grid.T:
        column_str = "".join(column)
        count += (column_str).count("XMAS")
        count += (column_str).count("SAMX")
    # Diagonals
    for i in range(int(-grid.shape[0] / 2) - 1, int(grid.shape[0] / 2) + 1):
        diagonal = "".join(grid.diagonal(i))
        antidiagonal = "".join(np.fliplr(grid).diagonal(i))
        count += (diagonal).count("XMAS")
        count += (diagonal).count("SAMX")
        count += (antidiagonal).count("XMAS")
        count += (antidiagonal).count("SAMX")
    return count


def part2(input: str) -> int:
    grid = parse_input(input)
    count = 0
    for i in range(grid.shape[0] - 2):
        for j in range(grid.shape[1] - 2):
            kernel = grid[i : i + 3, j : j + 3]
            if kernel[1, 1] != "A":
                continue
            if (
                kernel[0, 0] == "M"
                and kernel[0, 2] == "M"
                and kernel[2, 0] == "S"
                and kernel[2, 2] == "S"
            ):
                count += 1
                continue
            if (
                kernel[0, 0] == "S"
                and kernel[0, 2] == "S"
                and kernel[2, 0] == "M"
                and kernel[2, 2] == "M"
            ):
                count += 1
                continue
            if (
                kernel[0, 0] == "M"
                and kernel[0, 2] == "S"
                and kernel[2, 0] == "M"
                and kernel[2, 2] == "S"
            ):
                count += 1
                continue
            if (
                kernel[0, 0] == "S"
                and kernel[0, 2] == "M"
                and kernel[2, 0] == "S"
                and kernel[2, 2] == "M"
            ):
                count += 1
                continue
    return count


"""
Benchmark 1 (100 runs): ./venv/bin/python src/day04.py
    measurement          mean ± σ            min … max           outliers
    wall_time           100ms ± 6.08ms    94.4ms …  129ms          4 ( 4%)
    peak_rss           39.9MB ±  554KB    37.5MB … 41.2MB          7 ( 7%)
    cpu_cycles         2.86G  ±  129M     2.33G  … 2.99G           3 ( 3%)
    instructions       2.17G  ± 80.8M     1.85G  … 2.25G           3 ( 3%)
    cache_references   18.3M  ±  337K     17.9M  … 20.1M           5 ( 5%)
    cache_misses       1.44M  ±  351K     1.10M  … 2.80M          11 (11%)
    branch_misses      2.86M  ± 41.2K     2.78M  … 3.03M           5 ( 5%)
"""
if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_text = Path(sys.argv[1]).read_text()
    else:
        input_text = (
            Path(__file__).parent.parent / "inputs" / "2024" / "day04.txt"
        ).read_text()

    assert part1(EXAMPLE_INPUT) == 18
    result1 = part1(input_text)
    print(result1)

    assert part2(EXAMPLE_INPUT) == 9
    result2 = part2(input_text)
    print(result2)
