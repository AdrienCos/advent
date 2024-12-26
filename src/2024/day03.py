import enum
from pathlib import Path
import re
import sys

EXAMPLE_INPUT = (
    """xmul(2,4)&mul[3,7]!^don't()_mul(5,5)+mul(32,64](mul(11,8)undo()?mul(8,5))"""
)


def parse_input(input: str) -> str:
    return input.strip()


class OP(enum.Enum):
    MUL = 0
    DO = 1
    DONT = 2


def part1(input: str) -> int:
    ops = re.finditer(r"mul\((\d{1,3}),(\d{1,3})\)", input)
    sum = 0
    for op in ops:
        sum += int(op.group(1)) * int(op.group(2))
    return sum


def part2(input: str) -> int:
    mul_ops = [
        (e.start(), OP.MUL, e)
        for e in re.finditer(r"mul\((\d{1,3}),(\d{1,3})\)", input)
    ]
    do_ops = [(e.start(), OP.DO, e) for e in re.finditer(r"do\(\)", input)]
    dont_ops = [(e.start(), OP.DONT, e) for e in re.finditer(r"don't\(\)", input)]
    ops = sorted((mul_ops + do_ops + dont_ops), key=lambda x: x[0])
    filtered_ops: list[re.Match[str]] = []
    enabled = True
    for op in ops:
        if op[1] == OP.DO:
            enabled = True
        elif op[1] == OP.DONT:
            enabled = False
        elif op[1] == OP.MUL and enabled:
            filtered_ops.append(op[2])
        else:
            pass
    sum = 0
    for op in filtered_ops:
        sum += int(op.group(1)) * int(op.group(2))
    return sum


"""
Benchmark 1 (210 runs): python src/day03.py
    measurement          mean ± σ            min … max           outliers
    wall_time          23.7ms ± 3.87ms    20.5ms … 37.6ms         16 ( 8%)
    peak_rss           12.6MB ±  103KB    12.3MB … 12.8MB          1 ( 0%)
    cpu_cycles         62.5M  ± 9.62M        0   … 93.2M          25 (12%)
    instructions        105M  ± 15.7M        0   …  113M          26 (12%)
    cache_references    999K  ±  120K        0   … 1.14M           9 ( 4%)
    cache_misses       61.4K  ± 23.0K        0   …  191K           5 ( 2%)
    branch_misses       663K  ±  104K        0   …  726K          26 (12%)
"""
if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_text = Path(sys.argv[1]).read_text()
    else:
        input_text = (
            Path(__file__).parent.parent / "inputs" / "2024" / "day03.txt"
        ).read_text()

    assert part1(EXAMPLE_INPUT) == 161
    result1 = part1(input_text)
    print(result1)

    assert part2(EXAMPLE_INPUT) == 48
    result2 = part2(input_text)
    print(result2)
