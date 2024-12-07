from pathlib import Path
import sys


EXAMPLE_INPUT = """
3   4
4   3
2   5
1   3
3   9
3   3
"""


def parse_input(input: str) -> tuple[list[int], list[int]]:
    lines = input.strip().split("\n")
    left_list: list[int] = []
    right_list: list[int] = []
    for line in lines:
        left, right = line.split()
        left_list.append(int(left))
        right_list.append(int(right))
    return left_list, right_list


def part1(input: str) -> int:
    left, right = parse_input(input)
    left.sort()
    right.sort()
    total_distance = sum([abs(left[i] - right[i]) for i in range(len(left))])
    return total_distance


def part2(input: str) -> int:
    left, right = parse_input(input)
    score = 0
    for id in left:
        score += id * right.count(id)
    return score


"""
Benchmark 1 (153 runs): python src/day01.py
    measurement          mean ± σ            min … max           outliers
    wall_time          32.5ms ±  690us    31.5ms … 35.9ms          5 ( 3%)
    peak_rss           12.5MB ± 39.7KB    12.4MB … 12.6MB          3 ( 2%)
    cpu_cycles          133M  ± 2.05M      130M  …  141M           2 ( 1%)
    instructions        266M  ± 78.3K      266M  …  266M           7 ( 5%)
    cache_references   4.98M  ±  122K     4.81M  … 5.49M          10 ( 7%)
    cache_misses        342K  ±  121K      163K  …  734K           0 ( 0%)
    branch_misses       836K  ± 6.22K      824K  …  861K           6 ( 4%)
"""
if __name__ == "__main__":
    INPUT_TEXT = Path(sys.argv[1]).read_text()

    assert part1(EXAMPLE_INPUT) == 11
    result1 = part1(INPUT_TEXT)
    print(result1)

    assert part2(EXAMPLE_INPUT) == 31
    result2 = part2(INPUT_TEXT)
    print(result2)
