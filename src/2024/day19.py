from functools import cache
from pathlib import Path
import sys


EXAMPLE_INPUT = """
r, wr, b, g, bwu, rb, gb, br

brwrr
bggr
gbbr
rrbgbr
ubwu
bwurrg
brgr
bbrgwb
"""

type Towel = str
type Pattern = str


def parse_input(input: str) -> tuple[tuple[Towel, ...], tuple[Pattern, ...]]:
    towels_str, patterns_str = input.strip().split("\n\n")
    towels = tuple(towels_str.split(", "))
    patterns = tuple(patterns_str.split("\n"))
    return towels, patterns


@cache
def pattern_is_doable(pattern: Pattern, towels: tuple[Towel, ...]) -> bool:
    if len(pattern) == 0:
        return True

    is_doable = False
    for towel in towels:
        if pattern.startswith(towel):
            is_doable = is_doable or pattern_is_doable(pattern[len(towel) :], towels)
    return is_doable


@cache
def count_doable_patterns(pattern: Pattern, towels: tuple[Towel, ...]) -> int:
    if len(pattern) == 0:
        return 1

    count = 0
    for towel in towels:
        if pattern.startswith(towel):
            count += count_doable_patterns(pattern[len(towel) :], towels)
    return count


def part1(input: str) -> int:
    towels, patterns = parse_input(input)
    count = 0
    for pattern in patterns:
        if pattern_is_doable(pattern, towels):
            count += 1
    return count


def part2(input: str) -> int:
    towels, patterns = parse_input(input)
    count = 0
    for pattern in patterns:
        count += count_doable_patterns(pattern, towels)
    return count


"""
Benchmark 1 (8 runs): ./venv/bin/python src/day19.py /tmp/.sops4167395053/tmp-file721990689
    measurement          mean ± σ            min … max           outliers
    wall_time           626ms ± 10.3ms     614ms …  645ms          0 ( 0%)
    peak_rss           22.3MB ±  130KB    22.1MB … 22.5MB          0 ( 0%)
    cpu_cycles         2.29G  ± 21.3M     2.24G  … 2.30G           2 (25%)
    instructions       9.57G  ±  109M     9.32G  … 9.65G           2 (25%)
    cache_references   2.56M  ±  103K     2.42M  … 2.72M           0 ( 0%)
    cache_misses        571K  ±  115K      445K  …  728K           0 ( 0%)
    branch_misses      3.94M  ± 69.3K     3.83M  … 4.03M           0 ( 0%)
"""
if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_text = Path(sys.argv[1]).read_text()
    else:
        input_text = (
            Path(__file__).parent.parent / "inputs" / "2024" / "day19.txt"
        ).read_text()

    assert part1(EXAMPLE_INPUT) == 6
    result1 = part1(input_text)
    print(result1)

    assert part2(EXAMPLE_INPUT) == 16
    result2 = part2(input_text)
    print(result2)
