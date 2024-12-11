from collections import defaultdict
from functools import cache
from pathlib import Path
import sys


EXAMPLE_INPUT = """125 17"""

type Stones = dict[int, int]


def parse_input(input: str) -> Stones:
    stones: Stones = defaultdict(int)
    numbers = input.strip().split()
    for number_str in numbers:
        number = int(number_str)
        stones[number] += 1

    return stones


@cache
def split_stone(nb: int) -> tuple[int, int]:
    stone_str = str(nb)
    middle_idx = int(len(stone_str) / 2)
    left_stone = int(stone_str[:middle_idx])
    right_stone = int(stone_str[middle_idx:])
    return (left_stone, right_stone)


def blink(stones: Stones) -> Stones:
    new_stones: Stones = defaultdict(int)
    for stone, count in stones.items():
        # Rule 1: if the stone is 0, it becomes 1
        if stone == 0:
            new_stones[1] += count
        # Rule 2 : if the length of the number is even, split the stone in two
        elif len(str(stone)) % 2 == 0:
            left_stone, right_stone = split_stone(stone)
            new_stones[left_stone] += count
            new_stones[right_stone] += count
        # Rule 3 : multiply by 2024
        else:
            new_stones[stone * 2024] += count

    return new_stones


def part1(input: str) -> int:
    stones = parse_input(input)
    for _ in range(25):
        stones = blink(stones)
    count = sum(stones.values())
    return count


def part2(input: str) -> int:
    stones = parse_input(input)
    for _ in range(75):
        stones = blink(stones)
    count = sum(stones.values())
    return count


"""
Benchmark 1 (52 runs): ./venv/bin/python src/day11.py /tmp/.sops2530612852/tmp-file1496266942
    measurement          mean ± σ            min … max           outliers
    wall_time          96.4ms ± 3.90ms    91.2ms …  119ms          2 ( 4%)
    peak_rss           13.4MB ± 78.5KB    13.3MB … 13.6MB          0 ( 0%)
    cpu_cycles          402M  ± 6.33M      391M  …  426M           2 ( 4%)
    instructions        772M  ±  739K      771M  …  773M           0 ( 0%)
    cache_references   8.92M  ±  163K     8.53M  … 9.40M           1 ( 2%)
    cache_misses       1.01M  ±  174K      680K  … 1.64M           1 ( 2%)
    branch_misses      2.23M  ± 33.1K     2.17M  … 2.30M           0 ( 0%)
"""
if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_text = Path(sys.argv[1]).read_text()
    else:
        input_text = (Path(__file__).parent.parent / "inputs" / "day11.txt").read_text()

    assert part1(EXAMPLE_INPUT) == 55312
    result1 = part1(input_text)
    print(result1)

    result2 = part2(input_text)
    print(result2)
