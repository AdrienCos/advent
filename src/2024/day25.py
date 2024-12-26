from pathlib import Path
import sys


EXAMPLE_INPUT = """
#####
.####
.####
.####
.#.#.
.#...
.....

#####
##.##
.#.##
...##
...#.
...#.
.....

.....
#....
#....
#...#
#.#.#
#.###
#####

.....
.....
#.#..
###..
###.#
###.#
#####

.....
.....
.....
#....
#.#..
#.#.#
#####
"""

type Lock = tuple[int, int, int, int, int]
type Key = tuple[int, int, int, int, int]


def parse_input(input: str) -> tuple[list[Lock], list[Key]]:
    blocks = input.strip().split("\n\n")

    locks: list[Lock] = []
    keys: list[Key] = []
    for block_str in blocks:
        block_lines = block_str.split()
        block: list[int] = []
        for col_nb in range(len(block_lines[0])):
            col_value = -1
            for line_nb in range(len(block_lines)):
                if block_lines[line_nb][col_nb] == "#":
                    col_value += 1
            block.append(col_value)

        if len(block) != 5:
            raise IndexError
        block_value = tuple(block)
        if block_lines[0] == "#####":
            locks.append(block_value)  # type: ignore
        elif block_lines[6] == "#####":
            keys.append(block_value)  # type: ignore
        else:
            raise ValueError

    return locks, keys


def part1(input: str) -> int:
    locks, keys = parse_input(input)
    potential_matches = 0
    for key in keys:
        for lock in locks:
            is_compatible = True
            for column in range(5):
                if key[column] + lock[column] > 5:
                    is_compatible = False
                    break
            if is_compatible:
                potential_matches += 1
    return potential_matches


"""
Benchmark 1: ./venv/bin/python src/day25.py /var/folders/fm/891_8yt158b05hy09ypkjyt40000gn/T/.sops4205263516/tmp-file1023618495
    Time (mean ± σ):      59.4 ms ±   1.9 ms    [User: 47.8 ms, System: 8.6 ms]
    Range (min … max):    56.7 ms …  67.7 ms    40 runs
"""
if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_text = Path(sys.argv[1]).read_text()
    else:
        input_text = (
            Path(__file__).parent.parent / "inputs" / "2024" / "day25.txt"
        ).read_text()

    assert part1(EXAMPLE_INPUT) == 3
    result1 = part1(input_text)
    print(result1)
